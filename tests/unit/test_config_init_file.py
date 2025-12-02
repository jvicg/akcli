#!/usr/bin/env python3

"""
Suite of tests for `init_config_file` function.
"""

from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
import tomli
from rich.console import Console
from typer import Exit

from akcli.config import Config, _OptionsBase, init_config_file
from akcli.exceptions import UnableToGenerateConfigWarning

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def dummy_console():
    """
    Fixture that provides a mock Console object.
    """
    return MagicMock(spec=Console)


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """
    Fixture to reset the Config singleton instance before each test.
    """
    Config._instance = None


# ----------------------
# Tests
# ----------------------


def test_init_config_file_none(dummy_console):
    """
    Test that init_config_file does nothing when `value` is None.
    Should not raise Exit or any warnings.
    """
    init_config_file(None, dummy_console)


def test_init_config_file_success(dummy_console, dummy_open):
    """
    Test that init_config_file successfully generates the config file and calls print_info.
    """
    with (
        patch("akcli.config.Path.open", dummy_open, create=True),
        patch("akcli.config.tomli.load", return_value={}),
        patch("akcli.config.tomli_w.dump") as mock_dump,
        patch("akcli.config.print_info") as mock_print,
        pytest.raises(Exit),
    ):
        init_config_file(True, dummy_console)

    mock_dump.assert_called_once()
    mock_print.assert_called_once()


def test_init_config_file_warns_on_error(dummy_console):
    """
    Test that init_config_file raises UnableToGenerateConfigWarning
    if an exception occurs while writing the file.
    """
    with (
        patch("akcli.config.Path.open", side_effect=FileNotFoundError),
        pytest.warns(UnableToGenerateConfigWarning),
        pytest.raises(Exit),
    ):
        init_config_file(True, dummy_console)


def test_init_config_file_writes_correct_content(tmp_path, dummy_console):
    """
    Test that `init_config_file` writes the correct content to the config file.
    """
    tmp_file = tmp_path / "config.toml"

    # Create custom DummyOptions class to match our test data
    @dataclass
    class DummyOptions(_OptionsBase):
        edgerc_path: str = "/valid/path"
        edgerc_section: str = "default"
        proxy: Optional[str] = None

    # Create custom Config instance
    config = Config.__new__(Config)
    config._initialized = True
    config._path = tmp_file
    config.commands_name_class_map = {"main": DummyOptions}
    config._instance = config  # Ensure `__new__` returns this instance

    with pytest.raises(Exit):
        init_config_file(True, dummy_console, path=tmp_file)

    with tmp_file.open("rb") as f:
        content = tomli.load(f)

    assert "main" in content
    assert "edgerc_path" in content["main"]
    assert content["main"]["edgerc_path"] == "/valid/path"
    assert "edgerc_section" in content["main"]
    assert content["main"]["edgerc_section"] == "default"
    assert "proxy" not in content["main"]
