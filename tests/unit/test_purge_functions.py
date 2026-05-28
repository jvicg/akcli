#!/usr/bin/env python3

"""
Suite of tests for the `purge` command functions.
"""

import pytest

from akcli.commands.purge import _file_to_list, _validate_urls
from akcli.exceptions import InvalidParams

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def dummy_file(tmp_path):
    """Empty table to use as the main table in tests."""
    return tmp_path / "objects.txt"


# ----------------------
# Tests
# ----------------------


def test_validate_urls_dont_raise_error_on_valid_urls():
    """
    Test that the function doesn't raise an error when the string starts with http:// and https://
    """
    urls = ["https://example.com", "http://dummy.com"]
    _validate_urls(urls)


def test_validate_urls_raises_on_missing_scheme():
    """
    Test that the function raises InvalidParams when a URL doesn't include the protocol scheme.
    """
    with pytest.raises(InvalidParams):
        _validate_urls(["example.com"])


def test_validate_urls_raises_on_first_invalid_in_mixed_list():
    """
    Test that the function raises InvalidParams on the first invalid URL in a mixed list.
    """
    with pytest.raises(InvalidParams):
        _validate_urls(["https://valid.com", "invalid.com", "https://also-valid.com"])


def test_validate_urls_raises_on_partial_scheme():
    """
    Test that the function raises InvalidParams when the URL has a partial or malformed scheme.
    """
    with pytest.raises(InvalidParams):
        _validate_urls(["htp://example.com"])


def test_file_to_list_returns_correct_list(dummy_file):
    """
    Test that the function returns a correct list from a file with normal lines.
    """
    dummy_file.write_text("https://example.com\nhttps://dummy.com\n")
    assert _file_to_list(dummy_file) == ["https://example.com", "https://dummy.com"]


def test_file_to_list_discards_empty_lines(dummy_file):
    """
    Test that the function discards empty lines from the file.
    """
    dummy_file.write_text("https://example.com\n\nhttps://dummy.com\n")
    assert _file_to_list(dummy_file) == ["https://example.com", "https://dummy.com"]


def test_file_to_list_strips_whitespace(dummy_file):
    """
    Test that the function strips leading and trailing whitespace from each line.
    """
    dummy_file.write_text("  https://example.com  \n  https://dummy.com  \n")
    assert _file_to_list(dummy_file) == ["https://example.com", "https://dummy.com"]


def test_file_to_list_returns_empty_list_on_empty_file(dummy_file):
    """
    Test that the function returns an empty list when the file is empty.
    """
    dummy_file.write_text("")
    assert _file_to_list(dummy_file) == []
