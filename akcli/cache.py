#!/usr/bin/env python3

"""
Simple file-based cache implementation to cache HTTP requests.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from time import time
from typing import Any, Optional

from .__version__ import __title__
from .typing import CacheDB, GenericFunction, JSONResponse, Payload, SerializedCacheItem


@dataclass
class _CacheItem:
    """
    Dataclass representing a cached item. This dataclass provides methods to
    serialize and deserialize itself to/from a dictionary.
    """

    key: str
    data: JSONResponse
    ttl: float
    expires_at: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialize expires_at based on ttl if not provided."""
        if not hasattr(self, "expires_at") or self.expires_at is None:
            self.expires_at = time() + self.ttl

    @property
    def is_expired(self) -> bool:
        return time() > self.expires_at

    @classmethod
    def from_dict(cls, serialized_item: SerializedCacheItem) -> "_CacheItem":
        """Initialize a CacheItem from a dictionary."""
        item = cls(
            key=serialized_item["key"],
            data=serialized_item["data"],
            ttl=serialized_item["ttl"],
        )
        item.expires_at = serialized_item[
            "expires_at"
        ]  # Declare it after initialization since it doesn't belong to __init__
        return item

    def to_dict(self) -> SerializedCacheItem:
        """
        Serialize the CacheItem to a dictionary. `CacheItem.key` needs to be set
        as the key of the generated dictionary.
        """
        return {
            "key": self.key,  # Reduntantly store the key into the serialized obj
            "data": self.data,
            "ttl": self.ttl,
            "expires_at": self.expires_at,
        }


class Cache:
    """
    Simple file-based caching system to store and retrieve API responses.
    """

    def __init__(self, cache_dir: Path, ttl: float, use_cache: bool) -> None:
        self.ttl = ttl
        self.use_cache = use_cache
        self._cache_dir = cache_dir
        self._cache_file = self._cache_dir / f"{__title__}.cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Ensure the cache file exists
        if not self._cache_file.exists():
            self._cache_file.write_text("{}", encoding="utf-8")

    def _load_cache(self) -> CacheDB:
        with open(self._cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_cache(self, data: CacheDB) -> None:
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _cleanup(self, cache_db: CacheDB) -> None:
        """
        Remove expired items from the cache.
        """
        expired_keys = [
            k for k, v in cache_db.items() if _CacheItem.from_dict(v).is_expired
        ]

        for key in expired_keys:
            del cache_db[key]

        self._save_cache(cache_db)

    def get(self, key: str) -> Optional[_CacheItem]:
        """
        Retrieve a cached item by key. Returns None if not found or expired.
        """
        cache_db = self._load_cache()
        serialized_item = cache_db.get(key)
        self._cleanup(cache_db)  # Cleanup expired items

        # If the key is not found in cache
        if serialized_item is None:
            return None

        item = _CacheItem.from_dict(serialized_item)

        # Check if expired because the cache_db in memory has not been updated yet
        if not item.is_expired:
            return item

        # If gets to this point, the item is expired
        return None

    def set(self, item: _CacheItem) -> None:
        """
        Store a CacheItem in the cache db.
        """
        cache_db = self._load_cache()
        cache_db[item.key] = item.to_dict()
        self._save_cache(cache_db)

    def delete(self, key: str) -> None:
        """Remove an item from cache."""
        cache_db = self._load_cache()
        cache_db.pop(key, None)
        self._save_cache(cache_db)

    def generate_key(
        self, method: str, endpoint: str, payload: Optional[Payload]
    ) -> str:
        """
        Generate the cache key based on the request method, endpoint and payload.
        """
        s = (
            f"{method}-{endpoint}-{json.dumps(payload, default=str, sort_keys=True)}"
            if payload is not None
            else f"{method}-{endpoint}"
        )
        return hashlib.sha256(s.encode()).hexdigest()


# TODO: Consider if this decorator should be more generic
def cached(func: GenericFunction) -> GenericFunction:
    """
    Decorator that caches the result of a HTTP request.
    If a valid cached response exists, it is returned instead of performing the request.
    """

    @wraps(func)
    def wrapper(
        self, method: str, endpoint: str, *args: Any, **kwargs: Any
    ) -> SerializedCacheItem:
        payload = kwargs.get("json")
        cache: Cache = getattr(self, "_cache")
        key = cache.generate_key(method, endpoint, payload)

        cached = cache.get(key)
        if cached is not None and cache.use_cache:
            return cached.data

        # If not cached, make request to API and store result
        data = func(self, method=method, endpoint=endpoint, *args, **kwargs)
        cache_item = _CacheItem(key, data, cache.ttl)
        cache.set(cache_item)

        return data

    return wrapper  # type: ignore
