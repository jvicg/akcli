#!/usr/bin/env python

"""
Suite of tests functions for `_CacheItem` class.
"""

from time import sleep, time

import pytest

from akcli.cache import _CacheItem

# ----------------------
# Tests
# ----------------------


def test_item_is_initialize_with_expected_expired_at(
    cache_item_key, cache_item_data, ttl
):
    """
    Ensure that the `CacheItem` object generated `expired_at` property
    with a 0.5s error margin
    """
    item = _CacheItem(key=cache_item_key, data=cache_item_data, ttl=ttl)
    margin = 0.5
    now = time()
    assert item.expires_at == pytest.approx(now + item.ttl, abs=margin)


def test_item_expires(cache_item_key, cache_item_data):
    """
    Ensure that the `CacheItem` correctly identifies when it is expired.
    """
    cache_item = _CacheItem(key=cache_item_key, data=cache_item_data, ttl=0.25)
    assert not cache_item.is_expired
    sleep(0.5)
    assert cache_item.is_expired


def test_item_serialization_deserialization(cache_item_key, cache_item_data, ttl):
    """
    Ensure that the `CacheItem` can be serialized to a dictionary and deserialized back
    to an equivalent `CacheItem` object.
    """
    cache_item = _CacheItem(cache_item_key, cache_item_data, ttl)

    serialized_cache_item = cache_item.to_dict()
    deserialized_cache_item = _CacheItem.from_dict(serialized_cache_item)

    assert cache_item.key == deserialized_cache_item.key
    assert cache_item.data == deserialized_cache_item.data
    assert cache_item.ttl == deserialized_cache_item.ttl
    assert cache_item.expires_at == deserialized_cache_item.expires_at
    assert cache_item.is_expired == deserialized_cache_item.is_expired


def test_item_is_still_expired_after_deserialization(cache_item_key, cache_item_data):
    """
    Ensure that the `CacheItem` remains expired after being serialized and deserialized.
    """
    cache_item = _CacheItem(cache_item_key, cache_item_data, ttl=0.25)

    sleep(0.5)
    assert cache_item.is_expired

    serialized_cache = cache_item.to_dict()
    deserialized_cache = _CacheItem.from_dict(serialized_cache)

    assert deserialized_cache.is_expired
