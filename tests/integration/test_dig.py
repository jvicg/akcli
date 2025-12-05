#!/usr/bin/env python3

"""
Suite of integration tests for the `dig` subcommand.
"""

import pytest

from akcli.exceptions import DigNoAnswerWarning
from akcli.main import app

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def hostname():
    return "www.example.com"


# ----------------------
# Tests
# ----------------------


@pytest.mark.parametrize("query_type", ["A", "AAAA", "CNAME"])
def test_response_with_valid_credentials(
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


def test_response_with_invalid_credentials(
    https_server, edgerc_invalid, runner, hostname, cache_dir
):
    """
    Test the `dig` command with invalid credentials.
    """
    cmd = [
        "--edgerc",
        edgerc_invalid,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        hostname,
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "InvalidCredentials" in result.output


def test_response_when_no_records_found(https_server, edgerc, runner, cache_dir):
    """
    Test the `dig` command raises `DigNoAnswerWarning` when no records are found for the given hostname.
    """
    hostname = "invalid-domain.notexists"
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        hostname,
    ]

    with pytest.warns(DigNoAnswerWarning):
        result = runner.invoke(app, cmd)

    assert result.exit_code == 0


def test_response_fails_with_validate_certs(
    https_server, edgerc, runner, hostname, cache_dir
):
    """
    Test the `dig` command with certificate validation enabled fails since dummy server cert is self-signed.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--validate-certs",  # Force cert validation
        "dig",
        hostname,
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "RequestSSLError" in result.output


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


def test_response_with_timeout(https_server, edgerc, runner):
    """
    Test the `dig` command with a short timeout to simulate a timeout scenario.
    """
    cmd = [
        "--request-timeout",
        "1",
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "dig",
        "force-timeout",  # Hostname that triggers timeout in the test server
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "RequestTimeout" in result.output


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
