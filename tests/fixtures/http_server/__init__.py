#!/usr/bin/env python3

"""
Simple HTTPS server to simulate Akamai API and handle responses in the tests.
"""

from . import _endpoints  # noqa: F401 - Import it just to load the endpoints into the server
from ._http_server import run_https_server

__all__ = ["run_https_server"]
