#!/usr/bin/env python3

"""
Suite of integration tests for the `dig` subcommand.
"""

import pytest

from akcli.exceptions import DigNoAnswerWarning
from akcli.main import app
from tests.fixtures import (
    DIG_NO_RECORDS_HOSTNAME,
    DIG_VALID_HOSTNAME,
)

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def hostname():
    return DIG_VALID_HOSTNAME


# ----------------------
# Tests
# ----------------------


@pytest.mark.parametrize("query_type", ["A", "AAAA", "CNAME"])
def test_response_with_valid_query(
    https_server, edgerc, runner, hostname, cache_dir, query_type
):
    """
    Test the `dig` command with valid credentials and different query types.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        hostname,
        "--query-type",
        query_type,
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code == 0
    assert f"Result of query: {query_type} {hostname}" in result.output
    assert DIG_VALID_HOSTNAME in result.output
    assert "192.0.2.85" in result.output


def test_response_when_no_records_found(https_server, edgerc, runner, cache_dir):
    """
    Test the `dig` command raises `DigNoAnswerWarning` when no records are found for the given hostname.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        DIG_NO_RECORDS_HOSTNAME,
    ]

    with pytest.warns(DigNoAnswerWarning):
        result = runner.invoke(app, cmd)

    assert result.exit_code == 0


def test_response_with_missing_hostname(https_server, edgerc, runner, cache_dir):
    """
    Test the `dig` command with missing hostname argument.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "Missing argument 'HOSTNAME'" in result.output


def test_response_with_invalid_query_type(
    https_server, edgerc, runner, hostname, cache_dir
):
    """
    Test the `dig` command with an invalid query type.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        hostname,
        "--query-type",
        "INVALID",
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "Invalid value for '--query-type'" in result.output


def test_response_in_json_format(https_server, edgerc, runner, hostname, cache_dir):
    """
    Test the `dig` command with the output format set to JSON.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        hostname,
        "--json",
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code == 0
    assert "answerSection" in result.output
    assert "authoritySection" in result.output
    assert "result" in result.output
    assert "example.com" in result.output
    assert "recordType" in result.output


def test_response_with_raw_and_json_flags(
    https_server, edgerc, runner, hostname, cache_dir
):
    """
    Test that using --raw and --json simultaneously produces an error.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        hostname,
        "--raw",
        "--json",
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "MutuallyExclusiveArgs" in result.output
