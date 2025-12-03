#!/usr/bin/env python

"""
Suite of tests functions for `cached` decorator.
"""

from types import SimpleNamespace

import pytest

from akcli.cache import _CacheItem, cached

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def cached_data():
    return {"cached": "data"}


@pytest.fixture
def not_cached_data():
    return {"request": "executed"}


@pytest.fixture
def fake_cache(cached_data):
    """
    Create a fake Cache instance for testing purposes.
    """

    class FakeCache:
        def __init__(self):
            self.use_cache = True
            self.ttl = 300

            # Properties to make checks
            self.get_called = False
            self.set_called = False
            self.last_item_set = None
            self.last_key_generated = None
            self.cache_item_in_cache = True

        def get(self, key):
            self.get_called = True
            if self.cache_item_in_cache:
                return _CacheItem(key=key, data=cached_data, ttl=300)
            else:
                return None

        def set(self, item):
            self.set_called = True
            self.last_item_set = item

        def generate_key(self, method, endpoint, payload):
            self.last_key_generated = (method, endpoint, payload)
            return f"{method}-{endpoint}-dummyhash"

    return FakeCache()


@pytest.fixture
def fake_self(fake_cache):
    """
    Create a instace with a `_cache` attribute set to a fake Cache.
    """
    return SimpleNamespace(_cache=fake_cache)


@pytest.fixture
def dummy_func(not_cached_data):
    """
    Create a dummy function to be decorated with `cached` decorator.
    """
    calls = {"kwargs": None}

    def _dummy(self, method, endpoint, *args, **kwargs):
        _dummy.called = True
        calls["kwargs"] = kwargs  # type: ignore
        return not_cached_data

    _dummy.calls = calls
    _dummy.called = False
    return _dummy


@pytest.fixture
def decorated_cached_func(fake_self, dummy_func):
    """
    Dummy function decorated with `cached` decorator.
    """
    return cached(dummy_func).__get__(fake_self)


# ----------------------
# Tests
# ----------------------


def test_cached_returns_cached_item(
    fake_self, dummy_func, decorated_cached_func, cached_data, method, endpoint, payload
):
    """
    Ensure that the `cached` decorator retrieves the cached item when available.
    """
    cache = fake_self._cache

    result = decorated_cached_func(method, endpoint, payload)

    assert cache.get_called is True
    assert not cache.set_called
    assert not dummy_func.called
    assert result == cached_data


def test_cached_ignore_cache_if_use_cache_is_false(
    fake_self, dummy_func, decorated_cached_func, method, endpoint, not_cached_data
):
    """
    Ensure that the `cached` decorator ignores the cache when `use_cache` is False.
    """
    cache = fake_self._cache
    fake_self._cache.use_cache = False

    result = decorated_cached_func(method, endpoint)

    assert cache.set_called is True
    assert dummy_func.called is True
    assert result == not_cached_data


def test_cached_make_request_if_item_not_in_cache(
    fake_self, dummy_func, decorated_cached_func, method, endpoint, not_cached_data
):
    """
    Ensure that the `cached` decorator makes the request if item is not in cache.
    """
    cache = fake_self._cache
    cache.cache_item_in_cache = False

    result = decorated_cached_func(method, endpoint)

    assert cache.get_called is True
    assert cache.set_called is True
    assert dummy_func.called is True
    assert result == not_cached_data


def test_cached_generates_correct_key(
    fake_self, decorated_cached_func, method, endpoint, payload, not_cached_data
):
    """
    Ensure that the `cached` decorator generates the correct cache key.
    """
    cache = fake_self._cache
    cache.cache_item_in_cache = False

    expected_key_input = (method, endpoint, payload)
    expected_item = _CacheItem(
        key=f"{method}-{endpoint}-dummyhash", data=not_cached_data, ttl=cache.ttl
    )

    _ = decorated_cached_func(method, endpoint, json=payload)

    assert cache.last_key_generated == expected_key_input
    assert expected_item.key == cache.last_item_set.key
    assert expected_item.data == cache.last_item_set.data
    assert expected_item.ttl == cache.last_item_set.ttl
    assert isinstance(cache.last_item_set.key, str)


def test_cached_returns_dict_type(
    fake_self, decorated_cached_func, method, endpoint, cached_data, not_cached_data
):
    """
    Ensure that the `cached` decorator returns data in dict type no matter if cached or not.
    """
    cache = fake_self._cache

    result = decorated_cached_func(method, endpoint)

    assert isinstance(result, dict)
    assert result == cached_data

    cache.cache_item_in_cache = False

    result = decorated_cached_func(method, endpoint)

    assert isinstance(result, dict)
    assert result == not_cached_data


def test_cached_passes_kwargs(
    fake_self, decorated_cached_func, dummy_func, method, endpoint, payload
):
    """
    Ensure the cached decorator forwards kwargs to the wrapped function unchanged.
    """
    cache = fake_self._cache
    cache.cache_item_in_cache = False

    _ = decorated_cached_func(method, endpoint, json=payload, timeout=10)

    assert dummy_func.called is True
    assert dummy_func.calls["kwargs"] == {"json": payload, "timeout": 10}
