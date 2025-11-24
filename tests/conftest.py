#!/usr/bin/env python3

"""
Fixtures used in multiple test modules.
"""

import pytest

from akcli.cache import _CacheItem

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
