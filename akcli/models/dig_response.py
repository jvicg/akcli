#!/usr/bin/env python3

"""
Module that exposes the model `DigResponse` which defines the API response to the endpoint: /edge-diagnostics/v1/dig
Reference: https://techdocs.akamai.com/edge-diagnostics/reference/post-dig

Generated with `datamodel-code-generator` (https://github.com/koxudaxi/datamodel-code-generator)
and refined with manual adjustments.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from ._base import BaseAPIModel, BaseResponse


class BaseSectionItem(BaseAPIModel):
    preference_value: Optional[str] = Field(default=None)
    record_class: Optional[str] = Field(default=None)
    record_type: Optional[str] = Field(default=None)
    ttl: Optional[int] = Field(default=None)
    value: Optional[str] = Field(default=None)


class AnswerSectionItem(BaseSectionItem):
    hostname: str


class AuthoritySectionItem(BaseSectionItem):
    domain: str


AnswerSection = List[AnswerSectionItem]
AuthoritySection = List[AuthoritySectionItem]


class Result(BaseAPIModel):
    answer_section: AnswerSection = Field(default_factory=list)
    authority_section: AuthoritySection = Field(default_factory=list)
    raw_dig: Optional[str] = Field(alias="result", default=None)


class DigResponse(BaseResponse):
    internal_ip: Optional[str] = None
    result: Result
