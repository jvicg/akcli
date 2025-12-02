#!/usr/bin/env python3

"""
Suite of tests for `Config` class.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from tomli import TOMLDecodeError

from akcli.config import Config, _MainOptions
from akcli.exceptions import (
    FileUnableToParseWarning,
    InvalidConfigSectionWarning,
    InvalidOptionWarning,
)

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def data():
    """
    Fixture that provides dummy configuration data with both valid and invalid entries.
    """
    return {
        "main": {
            "edgerc_path": "/valid/path",
            "invalid_option": 1,
            "invalid_option2": 2,
        },
        "invalid_section": {"foo": "bar"},
    }


@pytest.fixture
def dummy_config(data):
    """
    Fixture that provides a Config instance with preloaded dummy data.
    """
    config = Config.__new__(Config)
    config._initialized = True
    config._data = data
    config.commands_name_class_map = {"main": _MainOptions}
    return config


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """
    Fixture to reset the Config singleton instance before each test.
    """
    Config._instance = None


# ----------------------
# Tests
# ----------------------


def test_singleton_behavior():
    """
    Test that Config class implements singleton behavior correctly.
    """
    config1 = Config()
    config2 = Config()
    assert config1 is config2


def test_config_init_only_once(monkeypatch, data, dummy_open):
    """
    Test that Config.__init__ is only called once due to singleton pattern.
    """
    call_init_count = {"count": 0}
    call_valid_count = {"count": 0}

    def fake_init_options(self):
        call_init_count["count"] += 1

    def fake_valid_sections(self):
        call_valid_count["count"] += 1

    monkeypatch.setattr(Config, "_init_options", fake_init_options)
    monkeypatch.setattr(Config, "_valid_sections", fake_valid_sections)

    with (
        patch("akcli.config.Path.open", new=dummy_open),
        patch("akcli.config.tomli.load", return_value=data),
    ):
        config1 = Config()
        config2 = Config()
        config3 = Config()

    assert config1 is config2
    assert config1 is config3
    assert call_init_count["count"] == 1
    assert call_valid_count["count"] == 1


@pytest.mark.filterwarnings("ignore::akcli.exceptions.InvalidConfigSectionWarning")
@pytest.mark.filterwarnings("ignore::akcli.exceptions.InvalidOptionWarning")
def test_load_config_success(data, dummy_open):
    """
    Test successful loading of a configuration file.
    """
    with (
        patch("akcli.config.Path.open", new=dummy_open),
        patch("akcli.config.tomli.load", return_value=data),
    ):
        config = Config()
        assert config._data == data


def test_load_config_file_not_found():
    """
    Test config returns an empty dictionary when the config file is not found.
    """
    with patch("akcli.config.Path.open", side_effect=FileNotFoundError):
        config = Config()
        assert config._data == {}


def test_load_config_empty_file(dummy_open):
    """
    Test config returns an empty dictionary when the config file is empty.
    """
    with (
        patch("akcli.config.Path.open", new=dummy_open),
        patch("akcli.config.tomli.load", return_value={}),
    ):
        config = Config()
        assert config._data == {}


def test_load_config_file_fail_decode(dummy_open):
    """
    Test that expected warning is raised when tomli raises an exception.
    """
    mock_decode_error = TOMLDecodeError(
        msg="mock decode error", doc="some invalid toml", pos=0
    )
    with (
        patch("akcli.config.Path.open", new=dummy_open),
        patch("akcli.config.tomli.load", side_effect=mock_decode_error),
        pytest.warns(FileUnableToParseWarning),
    ):
        Config()


def test_get_section_returns_empty_for_missing_section(dummy_config):
    """
    Test that _get_section returns an empty dict for a nonexistent section.
    """
    assert dummy_config._get_section("nonexistent") == {}


def test_extract_invalid_key(dummy_config):
    """
    Test that _extract_invalid_key correctly extracts invalid keys from TypeError messages.
    """
    e = TypeError("__init__() got an unexpected keyword argument 'foo'")
    assert dummy_config._extract_invalid_key(e) == "foo"

    e2 = TypeError("some weird error")
    assert dummy_config._extract_invalid_key(e2) == "<unknown>"


def test_valid_sections_warns_with_invalid_section(dummy_config):
    """
    Test that invalid sections in the configuration file, raises a warning.
    """
    with pytest.warns(InvalidConfigSectionWarning) as record:
        dummy_config._valid_sections()

    assert any("invalid_section" in str(warning.message) for warning in record)


def test_init_opts_warns_with_invalid_option(dummy_config):
    """
    Test that invalid options in the configuration file, raises a warning.
    """
    dummy_options_data = {
        "edgerc_path": "/dummy/path",
        "invalid_option": "some_value",
        "invalid_option2": 123,
    }

    with pytest.warns(InvalidOptionWarning) as record:
        opts = dummy_config._init_single_command_opts(
            "main", _MainOptions, dummy_options_data
        )

    for key in ["invalid_option", "invalid_option2"]:
        assert any(key in str(warning.message) for warning in record)

    assert opts.edgerc_path == Path("/dummy/path")


def test_init_options_with_mixed_data(dummy_config):
    """
    Test that both invalid sections and options raise appropriate warnings.
    """
    local_data = {
        "main": {"edgerc_path": "/valid/path", "invalid_option": 1},
        "invalid_section": {"foo": "bar"},
    }

    dummy_config._data = local_data

    with (
        pytest.warns(InvalidOptionWarning) as option_warnings,
        pytest.warns(InvalidConfigSectionWarning) as section_warnings,
    ):
        dummy_config._valid_sections()
        dummy_config._init_options()

    assert any("invalid_option" in str(w.message) for w in option_warnings)
    assert any("invalid_section" in str(w.message) for w in section_warnings)
    assert dummy_config.main.edgerc_path == Path("/valid/path")
