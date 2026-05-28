#!/usr/bin/env python3

"""
Suite of integration tests for the `purge` subcommand.
"""

from itertools import product

import pytest

from akcli.main import app
from tests.fixtures.constants import PURGE_BAD_REQUEST_TRIGGER, PURGE_EXPECTED_PURGE_ID

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def dummy_file(tmp_path):
    dummy_file = tmp_path / "objects.txt"
    dummy_file.write_text("https://example.com/image.jpg\nhttps://example.com/image2.jpg\n")
    return dummy_file


@pytest.fixture
def dummy_valid_url():
    return "https://example.com/image.jpg"


# ----------------------
# Tests
# ----------------------


def test_purge_fails_when_objects_and_from_file_passed_together(dummy_file, edgerc, cache_dir, tmp_path, runner):
    """
    Test `purge` command fails when mutually exclusive params are passed.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        "dummy_object",
        "--from-file",
        dummy_file,
    ]

    result = runner.invoke(app, cmd)

    assert result.exit_code != 0
    assert "MutuallyExclusiveArgs" in result.output


def test_purge_fails_when_no_objects_and_no_from_file(edgerc, cache_dir, runner):
    """
    Test `purge` command fails when neither objects nor --from-file are provided.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code != 0
    assert "InvalidParams" in result.output


def test_purge_fails_when_url_missing_scheme(edgerc, cache_dir, runner):
    """
    Test `purge` command fails when a URL is passed without http:// or https://.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        "example.com",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code != 0
    assert "InvalidParams" in result.output


def test_purge_fails_when_from_file_url_missing_scheme(edgerc, cache_dir, tmp_path, runner):
    """
    Test `purge` command fails when a file contains a URL without http:// or https://.
    """
    f = tmp_path / "objects.txt"
    f.write_text("not-valid.com\nhttps://valid.com\n")
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        "--from-file",
        f,
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code != 0
    assert "InvalidParams" in result.output


@pytest.mark.parametrize(
    "method, purge_type, network",
    list(product(["invalidate", "delete"], ["url", "tag", "cpcode"], ["production", "staging"])),
)
def test_purge_invalidate_url_staging(
    https_server, edgerc, cache_dir, runner, dummy_valid_url, method, purge_type, network
):
    """
    Test `purge` command succeeds for all combinations of --method, --purge-type and --network.
    Covers 12 combinations: 2 methods x 3 types x 2 networks.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        dummy_valid_url,
        "--method",
        method,
        "--purge-type",
        purge_type,
        "--network",
        network,
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert PURGE_EXPECTED_PURGE_ID in result.output


def test_purge_from_file(https_server, edgerc, cache_dir, tmp_path, runner, dummy_file):
    """
    Test `purge` command succeeds when objects are passed via --from-file.
    """
    f = tmp_path / "objects.txt"
    f.write_text("https://example.com/image.jpg\nhttps://example.com/image2.jpg\n")
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        "--from-file",
        f,
        "--purge-type",
        "url",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert PURGE_EXPECTED_PURGE_ID in result.output


def test_purge_json_output(https_server, edgerc, cache_dir, runner, dummy_valid_url):
    """
    Test `purge` command outputs valid JSON when --json flag is passed.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        dummy_valid_url,
        "--purge-type",
        "url",
        "--json",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert PURGE_EXPECTED_PURGE_ID in result.output
    assert "detail" in result.output
    assert "detail" in result.output
    assert "estimatedSeconds" in result.output
    assert "httpStatus" in result.output
    assert "supportId" in result.output


def test_purge_bad_request(https_server, edgerc, cache_dir, runner):
    """
    Test `purge` command fails with BadRequest when the API returns a 400.
    """
    cmd = [
        "--cache-dir",
        cache_dir,
        "--edgerc",
        edgerc,
        "--no-validate-certs",
        "purge",
        PURGE_BAD_REQUEST_TRIGGER,
        "--purge-type",
        "cpcode",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code != 0
    assert "BadRequest" in result.output
