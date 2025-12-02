#!/usr/bin/env python3

"""
Suite of tests for `_OptionsBase` class.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from akcli.config import _OptionsBase

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture()
def str_value():
    return "default"


@pytest.fixture()
def int_value():
    return 42


@pytest.fixture()
def bool_value():
    return True


@pytest.fixture()
def path_value():
    return Path("~/dummy/path")


@pytest.fixture()
def path_str_value():
    return "~/dummy/path_str"


@pytest.fixture()
def path_relative_value():
    return Path("relative/path")


@pytest.fixture
def dummy_options(
    str_value, int_value, bool_value, path_value, path_str_value, path_relative_value
):
    """
    Fixture that provides a dummy options dataclass for testing.
    """

    @dataclass
    class DummyOptions(_OptionsBase):
        option_str: str = str_value
        option_int: int = int_value
        option_bool: bool = bool_value
        option_path: Path = path_value
        option_path_str: Path = path_str_value  # type: ignore
        option_path_relative: Path = path_relative_value

    return DummyOptions()


# ----------------------
# Tests
# ----------------------


def test_iter_return_all_values(
    dummy_options,
    str_value,
    int_value,
    bool_value,
    path_value,
    path_str_value,
    path_relative_value,
):
    """
    Test that the dummy options dataclass can be iterated over its fields and values.
    """
    keys = {k: v for k, v in dummy_options}
    assert keys == {
        "option_str": str_value,
        "option_int": int_value,
        "option_bool": bool_value,
        "option_path": path_value.expanduser().resolve(),
        "option_path_str": Path(path_str_value).expanduser().resolve(),
        "option_path_relative": path_relative_value.resolve(),
    }


def test_options_has_expected_types(dummy_options):
    """
    Test that the dummy options dataclass has the expected default values.
    """
    assert isinstance(dummy_options.option_str, str)
    assert isinstance(dummy_options.option_int, int)
    assert isinstance(dummy_options.option_bool, bool)
    assert isinstance(dummy_options.option_path, Path)
    assert isinstance(dummy_options.option_path_str, Path)
    assert isinstance(dummy_options.option_path_relative, Path)


def test_options_path_expands_tilde(dummy_options, path_value, path_str_value):
    """
    Test that the path options correctly expand the tilde (~) to the user's home directory.
    """
    assert dummy_options.option_path == path_value.expanduser().resolve()
    assert dummy_options.option_path_str == Path(path_str_value).expanduser().resolve()


def test_options_path_resolves_relative(dummy_options, path_relative_value):
    """
    Ensure that the relative path option is resolved correctly.
    """
    expected_path = Path.cwd() / path_relative_value
    assert dummy_options.option_path_relative == expected_path.resolve()


def test_constructor_override_parses_path():
    """
    Test that overriding a path field in the constructor correctly parses the path.
    """

    @dataclass
    class Opts(_OptionsBase):
        path: Path = Path("~/overriden")

    opts = Opts(path="~/override")  # type: ignore
    assert opts.path == Path("~/override").expanduser().resolve()
