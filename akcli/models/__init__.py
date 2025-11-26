#!/usr/bin/env python3

"""
Pydantic models representing Akamai API responses.
"""

from .dig_response import DigResponse
from .translate_response import TranslateResponse

__all__ = [
    "DigResponse",
    "TranslateResponse",
]
