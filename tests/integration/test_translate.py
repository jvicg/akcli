#!/usr/bin/env python3

"""
Suite of integration tests for the `translate` subcommand.
"""

import pytest

from akcli.exceptions import TranslateNoLogsWarning
from akcli.main import app
from tests.fixtures import (
    TRANSLATE_30X_ID,
    TRANSLATE_BAD_REQUEST_ID,
    TRANSLATE_NO_LOGS_ID,
    TRANSLATE_NON_30X_ID,
)

# ----------------------
# Tests
# ----------------------


def test_translate_successful_with_30x_id(https_server, edgerc, cache_dir, runner):
    """
    Test `translate` command with a successful 30x ID.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "translate",
        TRANSLATE_30X_ID,
    ]

    result = runner.invoke(app, cmd)

    assert result.exit_code == 0
    assert f"Logs for Reference ID: {TRANSLATE_30X_ID}" in result.output
    assert "Certificate Error Details" in result.output
    assert "har-mock-server-dev.npe.hotstar-labs.com" in result.output


def test_translate_successful_no_30x_id(https_server, edgerc, cache_dir, runner):
    """
    Test `translate` command with a successful non-30x ID.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "translate",
        TRANSLATE_NON_30X_ID,
    ]

    result = runner.invoke(app, cmd)

    print(result.output)

    assert result.exit_code == 0
    assert f"Logs for Reference ID: {TRANSLATE_NON_30X_ID}" in result.output
    assert "example.com" in result.output
    assert "192.0.2.9" in result.output


def test_translate_pending_no_logs(https_server, edgerc, cache_dir, runner):
    """
    Test `translate` command with a pending ID and no logs available.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "translate",
        TRANSLATE_NO_LOGS_ID,
    ]

    with pytest.warns(TranslateNoLogsWarning):
        runner.invoke(app, cmd)


def test_translate_bad_request(https_server, edgerc, cache_dir, runner):
    """
    Test `translate` command with a bad request.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "translate",
        TRANSLATE_BAD_REQUEST_ID,
    ]

    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "BadRequest" in result.output


def test_translate_when_no_id_provided(https_server, edgerc, cache_dir, runner):
    """
    Test `translate` command when no ID is provided.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "translate",
    ]

    result = runner.invoke(app, cmd)

    assert result.exit_code == 2
    assert "Missing argument 'ID'" in result.output


def test_translate_with_json_output(https_server, edgerc, cache_dir, runner):
    """
    Test `translate` command with JSON output option.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "translate",
        TRANSLATE_30X_ID,
        "--json",
    ]

    result = runner.invoke(app, cmd)

    assert result.exit_code == 0
    # This data is present in the dummy json response
    assert '"createdBy": "jkowalski"' in result.output
    assert '"executionStatus": "SUCCESS"' in result.output
