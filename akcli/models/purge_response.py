# /usr/bin/env python3

"""
Generated with `datamodel-code-generator` (https://github.com/koxudaxi/datamodel-code-generator)
and refined with manual adjustments.
"""

from __future__ import annotations

from typing import Optional

from ._base import BaseAPIModel


class PurgeResponse(BaseAPIModel):
    detail: Optional[str] = None
    estimated_seconds: Optional[int] = None
    http_status: Optional[int] = None
    purge_id: Optional[str] = None
    support_id: Optional[str] = None
