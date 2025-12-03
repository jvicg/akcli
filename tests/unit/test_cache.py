#!/usr/bin/env python

"""
Suite of tests functions for `Cache` class.
"""

from time import sleep

import pytest

from akcli.cache import Cache, _CacheItem

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path


@pytest.fixture
def use_cache():
    return True


@pytest.fixture
def cache_params(cache_dir, ttl, use_cache):
    return {
        "cache_dir": cache_dir,
        "ttl": ttl,
        "use_cache": use_cache,
    }


@pytest.fixture
def cache(cache_params):
    return Cache(**cache_params)


# ----------------------
# Tests
# ----------------------


def test_file_is_created_on_init(cache_dir, ttl, use_cache):
    """
    Ensure that the cache file is created upon Cache initialization if it does not exist.
    """
    cache = Cache(cache_dir=cache_dir, ttl=ttl, use_cache=use_cache)

    assert cache._cache_file.exists()
    assert cache._cache_file.is_file()


def test_set(cache_params, cache_item):
    """
    Ensure that setting a cache item stores it correctly in the cache file.
    """
    cache = Cache(**cache_params)
    cache.set(cache_item)

    cache_db = cache._load_cache()

    assert cache_item.key in cache_db
    assert cache_db[cache_item.key]["key"] == cache_item.key
    assert cache_db[cache_item.key]["data"] == cache_item.data
    assert cache_db[cache_item.key]["ttl"] == cache_item.ttl
    assert cache_db[cache_item.key]["expires_at"] == cache_item.expires_at


def test_set_multiple_items(cache_params):
    """
    Ensure that multiple cache items can be set and retrieved correctly.
    """
    cache = Cache(**cache_params)

    items = [
        _CacheItem(key=f"key_{i}", data={"value": i}, ttl=100 + i) for i in range(5)
    ]

    for item in items:
        cache.set(item)

    cache_db = cache._load_cache()

    for item in items:
        assert item.key in cache_db
        assert cache_db[item.key]["data"] == item.data
        assert cache_db[item.key]["ttl"] == item.ttl
        assert cache_db[item.key]["expires_at"] == item.expires_at


def test_set_overwrites_existent_items(cache, cache_item, cache_item_key):
    """
    Test `set` overwrites item if a existent key is passed.
    """
    cache.set(cache_item)

    cache_item_new_data = {"new": "data"}
    cache_item_new_ttl = 25
    cache_item_new = _CacheItem(
        key=cache_item_key, data=cache_item_new_data, ttl=cache_item_new_ttl
    )
    cache.set(cache_item_new)

    cache_db = cache._load_cache()

    assert cache_db[cache_item_key]["data"] == cache_item_new_data
    assert cache_db[cache_item_key]["ttl"] == cache_item_new_ttl


def test_cleanup_removes_expired(cache, cache_item_key, cache_item_data):
    """
    Test that `_cleanup()` removes expired items.
    """
    cache_item = _CacheItem(cache_item_key, cache_item_data, 0.25)
    cache.set(cache_item)

    cache_db = cache._load_cache()
    assert cache_item.key in cache_db

    sleep(0.5)
    cache._cleanup(cache_db)

    # Load cache_db again to ensure changes took effect
    cache_db = cache._load_cache()
    assert cache_item.key not in cache_db


def test_cleanup_not_removes_valid(cache, cache_item):
    """
    Ensure that `_cleanup()` doesn't touch valid items.
    """
    cache.set(cache_item)
    cache_db = cache._load_cache()

    assert cache_item.key in cache_db

    cache._cleanup(cache_db)
    assert cache_item.key in cache_db
    assert cache_db[cache_item.key]["key"] == cache_item.key
    assert cache_db[cache_item.key]["data"] == cache_item.data
    assert cache_db[cache_item.key]["ttl"] == cache_item.ttl
    assert cache_db[cache_item.key]["expires_at"] == cache_item.expires_at


def test_get_returns_item_when_key_is_valid(cache, cache_item):
    """
    Test `get` returns a valid cache key.
    """

    cache.set(cache_item)
    get_cache_item = cache.get(cache_item.key)

    assert get_cache_item.key == cache_item.key
    assert get_cache_item.data == cache_item.data
    assert get_cache_item.ttl == cache_item.ttl
    assert get_cache_item.expires_at == cache_item.expires_at
    assert get_cache_item.is_expired == cache_item.is_expired


def test_get_returns_none_if_key_is_invalid(cache):
    """
    Ensure that `get` returns None if a invalid key is passed.
    """
    key = "invalid_key"
    cache_item = cache.get(key)

    assert cache_item is None


def test_get_returns_none_when_key_is_expired(cache, cache_item_key, cache_item_data):
    """
    Test `get` removes key from DB when is expired and returns None.
    """
    cache_item = _CacheItem(key=cache_item_key, data=cache_item_data, ttl=0.25)

    cache.set(cache_item)
    sleep(0.5)

    get_cache_item = cache.get(cache_item_key)
    cache_db = cache._load_cache()

    assert get_cache_item is None
    assert cache_item_key not in cache_db


def test_delete_removes_item(cache, cache_item, cache_item_key):
    """
    Ensure `delete` removes the cache item properly.
    """
    cache.set(cache_item)
    cache.delete(cache_item_key)

    assert cache_item_key not in cache._load_cache()


def test_delete_not_crash_on_nonexistent_keys(cache):
    """
    Ensure that `delete` can handle non-existent keys without errors.
    """
    cache.delete("non_existent_key")


def test_delete_removes_only_passed_key(cache, cache_item_data, ttl):
    """
    Ensure that the keys not passed to delete persists on DB after deleting others.
    """
    cache_item_delete_key = "delete_key"
    cache_item_not_delete_key = "key"
    cache_item_delete = _CacheItem(
        key=cache_item_delete_key, data=cache_item_data, ttl=ttl
    )
    cache_item_not_delete = _CacheItem(
        key=cache_item_not_delete_key, data=cache_item_data, ttl=ttl
    )

    cache.set(cache_item_delete)
    cache.set(cache_item_not_delete)

    cache.delete(cache_item_delete_key)

    cache_db = cache._load_cache()

    assert cache_item_delete_key not in cache_db
    assert cache_item_not_delete_key in cache_db


def test_generate_key_uniqueness(cache):
    """
    Ensure that `generate_key` produces unique keys for different inputs.
    """
    input1 = ("GET", "/api/resource1", None)
    input2 = ("POST", "/api/resource2", "payload")

    key1 = cache.generate_key(*input1)
    key2 = cache.generate_key(*input2)

    assert key1 != key2


@pytest.mark.parametrize(
    "payload2",
    [
        None,
        {"param": "value1"},
    ],
)
def test_generate_key_with_different_payloads(
    cache, method, endpoint, payload, payload2
):
    """
    Ensure that `generate_key` produces different keys for different payloads.
    """
    key1 = cache.generate_key(method, endpoint, payload)
    key2 = cache.generate_key(method, endpoint, payload2)

    assert key1 != key2


def test_generate_key_with_same_payload_in_different_order(cache, method, endpoint):
    """
    Ensure that `generate_key` produces the same key for payloads with same content
    but different order.
    """
    payload1 = {"a": 1, "b": 2}
    payload2 = {"b": 2, "a": 1}

    key1 = cache.generate_key(method, endpoint, payload1)
    key2 = cache.generate_key(method, endpoint, payload2)

    assert key1 == key2
