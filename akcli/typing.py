#!/usr/bin/env python3

"""
Type aliases used across the project.
"""

from typing import Any, Callable, Dict, List, Literal, Tuple, TypeVar

from requests.structures import CaseInsensitiveDict

_BaseDict = Dict[str, Any]
"""Generic dictionary with string keys and values of any type."""

JSONResponse = _BaseDict
"""Type alias representing a JSON response from the API."""

Certificate = Tuple[str, str]
"""Tuple representing certificate file paths (cert, key)."""

Headers = CaseInsensitiveDict
"""Case-insensitive dictionary for HTTP headers."""

Payload = _BaseDict
"""JSON payload for HTTP requests."""

SerializedCacheItem = _BaseDict
"""Dictionary representing a cached item in serialized JSON format."""

CacheDB = Dict[str, SerializedCacheItem]
"""Representation of the JSON cache file."""

SerializedOptions = _BaseDict
"""Serialized options in the configuration file. Each section will define the options of an subcommand."""

SerializedConfig = Dict[str, SerializedOptions]
"""Type alias representing the entire configuration file with all the options in serialized format."""

PanelType = Literal["info", "result", "warning", "error"]
"""String literals representing valid panel types for rich panels."""

ColumnHeaders = List[_BaseDict]
"""List of dictionaries defining the parameters for each column in a Rich Table."""

TableParams = _BaseDict
"""Defines a dictionary with the parameters to build a Rich Table."""

GenericFunction = TypeVar("GenericFunction", bound=Callable[..., Any])
"""Callable object that get any number of args and return any type."""
