#!/usr/bin/env python3

"""
Pydantic models representing Akamai API responses.
"""

from .base_response import BaseResponse
from .dig_response import DigResponse
from .translate_response import TranslateResponse

__all__ = [
    "BaseResponse",
    "DigResponse",
    "TranslateResponse",
]
