#!/usr/bin/env python3

"""
Fixtures used in the tests that contains HTTPS server, constants and files with test data.
"""

from .constants import (
    ACCESS_TOKEN,
    CERT,
    CLIENT_TOKEN,
    DIG_NO_RECORDS_RESPONSE,
    DIG_SUCCESS_RESPONSE,
    EDGERC_TEMPLATE,
    INVALID_ACCESS_TOKEN,
    INVALID_CLIENT_TOKEN,
    PRIV_KEY,
)
from .http_server import run_https_server

__all__ = [
    "ACCESS_TOKEN",
    "CERT",
    "CLIENT_TOKEN",
    "DIG_SUCCESS_RESPONSE",
    "DIG_NO_RECORDS_RESPONSE",
    "EDGERC_TEMPLATE",
    "INVALID_ACCESS_TOKEN",
    "INVALID_CLIENT_TOKEN",
    "PRIV_KEY",
    "run_https_server",
]
