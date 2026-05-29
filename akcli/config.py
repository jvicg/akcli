#!/usr/bin/env python3

"""
Provides utilities for loading, parsing, and managing the configuration file,
and defines all the default configuration values used on the CLI.
"""

import warnings
from dataclasses import asdict, dataclass, field, fields
from functools import cached_property
from inspect import isclass
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple, Type, Union, get_type_hints

import tomli
import tomli_w
import typer
from platformdirs import user_cache_dir, user_config_dir
from rich.console import Console
from typing_extensions import Self

from .__version__ import __title__
from .exceptions import (
    FileUnableToParseWarning,
    InvalidConfigSectionWarning,
    InvalidOptionWarning,
    UnableToGenerateConfigWarning,
)
from .typing import SerializedConfig, SerializedOptions
from .utils import highlight, print_info

_CONFIG_FILE_PATH = Path(user_config_dir()) / __title__ / "config.toml"
_CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

_DEFAULT_PROXY = None
_DEFAULT_EDGERC_PATH = Path.home() / ".edgerc"
_DEFAULT_EDGERC_SECTION = "default"
_DEFAULT_CACHE_DIR = Path(user_cache_dir())
_DEFAULT_CACHE_TTL = 300
_DEFAULT_USE_CACHE = True
_DEFAULT_REQUEST_TIMEOUT = 15
_DEFAULT_VALIDATE_CERTS = True

_DEFAULT_DIG_QUERY_TYPE = "A"
_DEFAULT_DIG_RAW = False
_DEFAULT_DIG_SHORT_OUTPUT = False

_DEFAULT_TRANSLATE_TRACE = False

_DEFAULT_PURGE_METHOD = "invalidate"
_DEFAULT_PURGE_NETWORK = "staging"
_DEFAULT_PURGE_TYPE = "url"

_DEFAULT_NL_LIST_LIST_TYPE = "ip"
_DEFAULT_NL_LIST_SEARCH = None
_DEFAULT_NL_LIST_INCLUDE_ELEMENTS = False
_DEFAULT_NL_LIST_EXTENDED = False

MIN_REQUEST_TIMEOUT = 0
MAX_REQUEST_TIMEOUT = 120


@dataclass
class _OptionsBase:
    """
    Base dataclass for all CLI command options.
    This class is responsible of parsing the parameters in the config file into the expected types.
    """

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """
        Make the dataclass iterable to loop over its fields and values.
        """
        for f in fields(self):
            yield f.name, getattr(self, f.name)

    def __post_init__(self) -> None:
        """
        Parse field values into their expected types after initialization.

        Nested `_OptionsBase` subclasses are parsed from dicts (as returned by the TOML config file),
        and `Path` fields are expanded and resolved from strings.
        """
        type_hints = get_type_hints(self.__class__)
        for field_name, field_value in self:
            expected_type = type_hints.get(field_name)

            # Parse dicts into `_OptionsBase`
            if isclass(expected_type) and issubclass(expected_type, _OptionsBase) and isinstance(field_value, Dict):
                parsed_value = expected_type(**field_value)
                setattr(self, field_name, parsed_value)

            # Only parse `Path`s, or `str`s that are intended to be `Path`
            if expected_type is Path and isinstance(field_value, (str, Path)):
                parsed_value = Path(field_value).expanduser().resolve()
                setattr(self, field_name, parsed_value)

    @classmethod
    def from_config(cls, cmd_name: str, data: SerializedConfig) -> Self:
        """
        Instantiate the class from a config file, filtering out invalid fields.

        Recursively validates nested `_OptionsBase` subclasses, so invalid options
        at any depth are caught and warned about. Valid fields are passed to the constructor;
        invalid ones are ignored and an `InvalidOptionWarning` is emitted for each.
        """
        type_hints = get_type_hints(cls)
        valid_fields = {f.name: type_hints.get(f.name) for f in fields(cls)}
        filtered, invalid = {}, []

        for key in data:
            if key in valid_fields:
                current_param_type = valid_fields.get(key, "")
                # Recursively call the function if param is expected as `_OptionsBase`
                if isclass(current_param_type) and issubclass(current_param_type, _OptionsBase):
                    filtered[key] = current_param_type.from_config(key, data[key])

                else:
                    filtered[key] = data[key]

            else:
                invalid.append(key)

        for key in invalid:
            warnings.warn(
                f"Ignoring invalid config option '{highlight(key)}' in '{cmd_name}'.",
                InvalidOptionWarning,
                stacklevel=2,
            )

        return cls(**filtered)


@dataclass
class _MainOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli` main command.
    """

    edgerc_path: Path = _DEFAULT_EDGERC_PATH
    edgerc_section: str = _DEFAULT_EDGERC_SECTION
    cache_dir: Path = _DEFAULT_CACHE_DIR
    cache_ttl: float = _DEFAULT_CACHE_TTL
    use_cache: bool = _DEFAULT_USE_CACHE
    request_timeout: int = _DEFAULT_REQUEST_TIMEOUT
    validate_certs: bool = _DEFAULT_VALIDATE_CERTS
    proxy: Optional[str] = _DEFAULT_PROXY


@dataclass
class _DigOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli dig` command.
    """

    query_type: str = _DEFAULT_DIG_QUERY_TYPE
    raw: bool = _DEFAULT_DIG_RAW
    short_output: bool = _DEFAULT_DIG_SHORT_OUTPUT


@dataclass
class _TranslateOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli translate` command.
    """

    trace: bool = _DEFAULT_TRANSLATE_TRACE


@dataclass
class _PurgeOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli purge` command.
    """

    method: str = _DEFAULT_PURGE_METHOD
    network: str = _DEFAULT_PURGE_NETWORK
    type: str = _DEFAULT_PURGE_TYPE


@dataclass
class _NLListOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli nl list` command.
    """

    list_type: str = _DEFAULT_NL_LIST_LIST_TYPE
    search: Optional[str] = _DEFAULT_NL_LIST_SEARCH
    include_elements: bool = _DEFAULT_NL_LIST_INCLUDE_ELEMENTS
    extended: bool = _DEFAULT_NL_LIST_EXTENDED


@dataclass
class _NLOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli nl` command.
    """

    list: _NLListOptions = field(default_factory=_NLListOptions)


class Config:
    """
    Handle configuration file loading and initialization and exposing all the config options.

    The exposed properties are `_OptionsBase` objects of each command and they are initialized
    with the options found in the config file or the default values if not present in config file.

    This class implements the Singleton pattern to ensure only one instance exists across the application.
    """

    _instance = None

    """
    NOTE: Declare commands options at class level allows `dataclasses.get_type_hints()`
    to automatically discover all commands and their type. This helps to validate config file
    parameters without needing to hardcode the valid sections.
    """

    main: _MainOptions
    dig: _DigOptions
    translate: _TranslateOptions
    purge: _PurgeOptions
    nl: _NLOptions

    def __new__(cls, *args: Any, **kwargs: Any) -> "Config":
        """
        Singleton implementation to ensure only one instance of Config exists.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Avoid calling `__init__` multiple times
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True

        self._path = _CONFIG_FILE_PATH
        self._data = self._load_config()

        # Validate config file and initialize `_OptionsBase` objects
        self._valid_sections()
        self._init_options()

    def _load_config(self) -> SerializedConfig:
        """
        Load and parse the configuration file.
        """
        try:
            with self._path.open("rb") as f:
                return tomli.load(f)

        except FileNotFoundError:
            return {}

        # If the config file cannot be parsed, print a warning and return an empty dict
        except tomli.TOMLDecodeError as e:
            warnings.warn(f"Error parsing config file: {e}", FileUnableToParseWarning, stacklevel=2)
            return {}

    def _get_section(self, section: str) -> SerializedOptions:
        """
        Get a specific option from the configuration.
        """
        return self._data.get(section, {})

    def _valid_sections(self) -> None:
        """
        Detect unrecognized sections in the configuration file and print warning if found some.
        Each section in the config file must represent an existent command.
        """
        for section in self._data:
            if section not in self.commands_name_class_map:
                warnings.warn(
                    f"Ignoring invalid config section '{highlight(section)}'.",
                    InvalidConfigSectionWarning,
                    stacklevel=2,
                )

    @cached_property
    def commands_name_class_map(self) -> Dict[str, Type[_OptionsBase]]:
        """
        Dictionary containing the name of the command followed by the class which contains its options,
        This property is used by `_valid_sections`, `_init_options` and `init_config_file` methods.
        """
        hints = get_type_hints(self.__class__)
        commands_map = {name: typ for name, typ in hints.items() if issubclass(typ, _OptionsBase)}
        return commands_map

    def _init_options(self) -> None:
        """
        Initialize all command options from the config file, ignoring invalid parameters.
        """
        for cmd_name, cmd_class in self.commands_name_class_map.items():
            section_data = self._get_section(cmd_name)
            setattr(
                self,
                cmd_name,
                # `_OptionsBase.from_config()` will handle the params validation
                cmd_class.from_config(cmd_name, section_data),
            )


def _to_serializable_dict(obj: Union[_OptionsBase, Dict]) -> SerializedOptions:
    """
    Recursively convert an `_OptionsBase` instance or dict into a serializable dict.

    Converts `Path` fields to strings, removes `None` values, and recursively
    processes nested dicts. Required since `tomli_w` only supports primitive types.
    """
    d = (
        asdict(obj) if isinstance(obj, _OptionsBase) else obj
    )  # `asdict()` recursively converts nested `_OptionsBase`` to dicts, so inner levels will be always dicts

    for k, v in d.copy().items():  # Iterate over a copy to allow safe deletion of keys
        # If obj is a dict, recursively call the function to serialize inner elements
        if isinstance(v, dict):
            d[k] = _to_serializable_dict(v)

        elif isinstance(v, Path):
            d[k] = str(v)

        # If the value is None remove it from the dict, since NoneType is not serializable
        elif v is None:
            del d[k]

    return d


def init_config_file(value: Optional[bool], console: Console, path: Path = _CONFIG_FILE_PATH) -> None:
    """
    Generate a default configuration file and exit program.
    """
    if value is None:
        return

    highlighted_path = highlight(str(path))

    config = Config()
    # Initialize each `_OptionsBase` class with no arguments to get default values,
    # ignoring any user-defined config that may already exist.
    default_config = {name: _to_serializable_dict(cls()) for name, cls in config.commands_name_class_map.items()}

    # Ask for confirmation in case config file already exists
    if path.exists():
        overwrite = typer.confirm(f"Config file already exists at {path}. Overwrite?")
        if not overwrite:
            raise typer.Exit()

    try:
        with path.open("wb") as f:
            tomli_w.dump(default_config, f)

        print_info(console, f"Succesfully generated config file at {highlighted_path}")

    # Print a warning if, for any reason, unable to generate the config file
    except Exception:
        warnings.warn(
            f"Unable to generate the configuration file at {highlighted_path}",
            UnableToGenerateConfigWarning,
            stacklevel=2,
        )

    raise typer.Exit()
