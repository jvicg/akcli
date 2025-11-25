#!/usr/bin/env python3

"""
Provides utilities for loading, parsing, and managing the configuration file,
and defines all the default configuration values used on the CLI.
"""

from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass, fields
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple, Type, get_type_hints

import tomli
import tomli_w
from platformdirs import user_cache_dir, user_config_dir
from rich.console import Console
from typer import Exit

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
_DEFAULT_DIG_SHORT_OUTPUT = False

_DEFAULT_TRANSLATE_TRACE = False

MIN_REQUEST_TIMEOUT = 0
MAX_REQUEST_TIMEOUT = 120


@dataclass
class _OptionsBase:
    """
    Base dataclass used to build other Options dataclasses.
    This class is responsible of parsing the parameters in the config file into the expected types.
    """

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """
        Make the dataclass iterable to loop over its fields and values.
        """
        for field in fields(self):
            yield field.name, getattr(self, field.name)

    def __post_init__(self) -> None:
        """
        Parse paths into `Path` objs and expand the tilde (~) after initialization.
        """
        type_hints = get_type_hints(self.__class__)
        for field_name, field_value in self:
            expected_type = type_hints.get(field_name)

            # Only parse `Path`s, or `str`s that are intended to be `Path`
            if expected_type is Path and isinstance(field_value, (str, Path)):
                parsed_value = Path(field_value).expanduser().resolve()
                setattr(self, field_name, parsed_value)


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
    short_output: bool = _DEFAULT_DIG_SHORT_OUTPUT


@dataclass
class _TranslateOptions(_OptionsBase):
    """
    Dataclass that contains all the options for the `akcli translate` command.
    """

    trace: bool = _DEFAULT_TRANSLATE_TRACE


class Config:
    """
    Handle configuration file loading and initialization and exposing all the config options.

    The exposed properties are `_OptionsBase` objects of each command and they are initialized
    with the options found in the config file or the default values if not present in config file.

    This class implements the Singleton pattern to ensure only one instance exists across the application.
    """

    _instance = None

    """
    Declare commands options at class level allows `dataclasses.get_type_hints()` 
    to automatically discover all commands and their type. This helps to validate config file 
    parameters without needing to hardcode the valid sections/options.
    """

    main: _MainOptions
    dig: _DigOptions
    translate: _TranslateOptions

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
            warnings.warn(f"Error parsing config file: {e}", FileUnableToParseWarning)
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
                # print_warning(
                #     self._console, f"Ignoring invalid config section '{section}'."
                # )
                warnings.warn(
                    f"Ignoring invalid config section '{highlight(section)}'.",
                    InvalidConfigSectionWarning,
                )

    def _extract_invalid_key(self, e: TypeError) -> str:
        """
        Helper method to extract the invalid key from `TypeError` msg by spliting it by single quote (').
        Example TypeError msg: "__init__() got an unexpected keyword argument 'foo'"
        """
        try:
            return str(e).split("'")[1]
        except IndexError:
            return "<unknown>"

    """
    NOTE: These three methods may add some complexity to the class, but in return provides an automatic and extensible
    mechanism for validating configuration parameters. New commands only need to be declared type-annotated attributes
    at the class level, and they will be discovered and validated without requiring manual updates elsewhere.
    """

    @cached_property
    def commands_name_class_map(self) -> Dict[str, Type[_OptionsBase]]:
        """
        Dictionary containing the name of the command followed by the class which contains its options,
        This property is used by `_valid_sections`, `_init_options` and `init_config_file` methods.
        """
        hints = get_type_hints(self.__class__)
        commands_map = {
            name: typ for name, typ in hints.items() if issubclass(typ, _OptionsBase)
        }
        return commands_map

    def _init_single_command_opts(
        self, name: str, cls: Type[_OptionsBase], data: SerializedOptions
    ) -> _OptionsBase:
        """
        Initialize a single command options object ignoring invalid parameters in the config,
        and printing a warning with the invalid params.
        """
        data_copy = data.copy()  # Don't modify the original dict
        while True:
            try:
                return cls(**data_copy)
            except TypeError as e:
                key = self._extract_invalid_key(e)
                warnings.warn(
                    f"Ignoring invalid config option '{highlight(key)}' in '{name}'.",
                    InvalidOptionWarning,
                )
                data_copy.pop(key, None)

    def _init_options(self) -> None:
        """
        Initialize all command options from the config file, ignoring invalid parameters.
        """
        for cmd_name, cmd_class in self.commands_name_class_map.items():
            section_data = self._get_section(cmd_name)
            setattr(
                self,
                cmd_name,
                self._init_single_command_opts(cmd_name, cmd_class, section_data),
            )


def _to_serializable_dict(obj: _OptionsBase) -> SerializedOptions:
    """
    Helper function to convert dataclass items back to a serializable types.
    This is needed since `tomli_w` does not support complex types, such as `Path`.
    """
    d = asdict(obj)
    for k, v in d.copy().items():  # Iterate over a copy of the dict obj
        if isinstance(v, Path):
            d[k] = str(v)

        # If the value is None remove it from the dict, since NoneType is not serializable
        elif v is None:
            del d[k]

    return d


def init_config_file(value: Optional[bool], console: Console) -> None:
    """
    Generate a default configuration file and exit program.
    """
    if value is None:
        return

    path = _CONFIG_FILE_PATH
    highlighted_path = highlight(str(path))

    # Initilialize config and build default config dict
    config = Config()
    default_config = {
        name: _to_serializable_dict(cls())
        for name, cls in config.commands_name_class_map.items()
    }

    try:
        with path.open("wb") as f:
            tomli_w.dump(default_config, f)

        print_info(console, f"Succesfully generated config file at {highlighted_path}")

    # Print a warning if unable to generate the config file
    except Exception:
        warnings.warn(
            f"Unable to generate the configuration file at {highlighted_path}",
            UnableToGenerateConfigWarning,
        )

    raise Exit()
