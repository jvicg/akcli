#!/usr/bin/env python3

"""
Suite of integration tests for general CLI behaviors.

These tests use the `dig` subcommand as a vehicle to test behaviors
shared across all subcommands: authentication, SSL validation, timeouts, etc.

Since all subcommands use the same underlying Akamai API client, these behaviors
are only tested here and not repeated in any other subcommand test suites.
"""

from akcli.main import app
from tests.fixtures import DIG_TIMEOUT_HOSTNAME, DIG_VALID_HOSTNAME


def test_response_with_invalid_credentials(
    https_server, edgerc_invalid, runner, cache_dir
):
    """
    Test that invalid credentials produce an authentication error.
    """
    cmd = [
        "--edgerc",
        edgerc_invalid,
        "--cache-dir",
        cache_dir,
        "--no-validate-certs",
        "dig",
        DIG_VALID_HOSTNAME,
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "InvalidCredentials" in result.output


def test_response_fails_with_validate_certs(https_server, edgerc, runner, cache_dir):
    """
    Test that certificate validation fails when the server uses a self-signed certificate.
    """
    cmd = [
        "--edgerc",
        edgerc,
        "--cache-dir",
        cache_dir,
        "--validate-certs",
        "dig",
        DIG_VALID_HOSTNAME,
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "RequestSSLError" in result.output


def test_response_with_timeout(https_server, edgerc, runner):
    """
    Test that the request timeout is honored when the server takes too long to respond.
    """
    cmd = [
        "--request-timeout",
        "1",
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "dig",
        DIG_TIMEOUT_HOSTNAME,
    ]
    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "RequestTimeout" in result.output
