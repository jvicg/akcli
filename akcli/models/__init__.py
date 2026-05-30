#!/usr/bin/env python3

"""
Pydantic models representing Akamai API responses.
"""

from ._base import BaseAPIModel
from .dig_response import DigResponse
from .nl_response import NetworkList, NLListResponse
from .purge_response import PurgeResponse
from .translate_response import TranslateResponse

__all__ = ["BaseAPIModel", "DigResponse", "NLListResponse", "NetworkList", "PurgeResponse", "TranslateResponse"]
