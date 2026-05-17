#!/usr/bin/env python3

"""
Fixtures used in multiple test modules.
"""

from unittest.mock import mock_open

import pytest
from typer.testing import CliRunner

from akcli.cache import _CacheItem
from tests.fixtures import (
    ACCESS_TOKEN,
    CLIENT_TOKEN,
    EDGERC_TEMPLATE,
    INVALID_ACCESS_TOKEN,
    INVALID_CLIENT_TOKEN,
    run_https_server,
)

# -----------------------
# General fixtures
# -----------------------


@pytest.fixture
def method():
    return "GET"


@pytest.fixture
def endpoint():
    return "/api/resource"


@pytest.fixture
def payload():
    return {"foo": "bar"}


@pytest.fixture
def dummy_open():
    return mock_open(read_data="dummy-content")


# -----------------------
# Cache fixtures
# -----------------------


@pytest.fixture
def cache_item_key():
    return "test_key"


@pytest.fixture()
def cache_item_data():
    return {"foo": "bar"}


@pytest.fixture
def ttl():
    return 300


@pytest.fixture
def cache_item(cache_item_key, cache_item_data, ttl):
    return _CacheItem(key=cache_item_key, data=cache_item_data, ttl=ttl)


# -----------------------
# Integration fixtures
# -----------------------


@pytest.fixture
def runner():
    """Typer CLI runner for invoking commands in tests."""
    return CliRunner()


@pytest.fixture
def cache_dir(tmp_path):
    """Use a different temporary cache directory for each test."""
    return tmp_path


@pytest.fixture
def https_server():
    """
    Fixture that provides a simple HTTPS server for testing.
    Yields the server address in the format `host:port`.
    """

    with run_https_server() as server:
        yield "{0}:{1}".format(*server.socket.getsockname())


"""
NOTE: The edgerc fixtures generate edgerc files on-the-fly using a template to ensure
they point to the correct HTTPS server address, since the server uses dynamic port assignment.
We could have used a fixed port, but using dynamic ports helps avoid potential port conflicts.

Since edgerc fixtures already content https_server, tests using them do not need to also use
the https_server fixture directly, but still will be passed to tests to maintain clarity.
"""


def _gen_edgerc_content(https_server: str, access_token: str, client_token: str) -> str:
    """
    Helper function to generate `edgerc` file content using a template.
    """
    return (
        EDGERC_TEMPLATE.read_text()
        .format(
            https_server=https_server,
            access_token=access_token,
            client_token=client_token,
        )
        .strip()
    )


@pytest.fixture
def edgerc(tmp_path, https_server):
    """Fixture that provides a valid edgerc file content."""
    content = _gen_edgerc_content(https_server, ACCESS_TOKEN, CLIENT_TOKEN)
    edgerc = tmp_path / ".edgerc"
    edgerc.write_text(content)

    return edgerc


@pytest.fixture
def edgerc_invalid(tmp_path, https_server):
    """Fixture that provides an invalid edgerc file content."""
    content = _gen_edgerc_content(
        https_server, INVALID_ACCESS_TOKEN, INVALID_CLIENT_TOKEN
    )
    edgerc = tmp_path / ".edgerc"
    edgerc.write_text(content)

    return edgerc
