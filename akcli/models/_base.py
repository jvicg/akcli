#!/usr/bin/env python3

"""
Module defining the base models and common API components.

This module provides:
- A base model for all API responses, handling validation and camel case aliases.
- Common models and types shared across the API.
"""

from __future__ import annotations

from typing import Optional, Type, TypeVar

from pydantic import BaseModel, Field
from pydantic_core import ValidationError

from ..exceptions import InvalidResponse
from ..typing import JSONResponse
from ..utils import snakecase_to_camel

# ----------------------
# Base Model
# ----------------------

_T = TypeVar("_T", bound="BaseAPIModel")
"""Type variable used to represent any subclass of `BaseAPIModel`."""


class BaseAPIModel(BaseModel):
    """
    Base model that set the base alias to camel case to match API format.
    This is the base model for build all the rest of models, since all API
    responses return values with camel case.
    """

    @classmethod
    def parse_model(cls: Type[_T], data: JSONResponse) -> _T:
        """
        Parse API JSON response into Pydantic model handling possible exceptions.
        """
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            raise InvalidResponse(f"Data validation error: {e}")

    class Config:
        alias_generator = snakecase_to_camel
        validate_by_name = True


# ----------------------
# Common Models
# ----------------------


class EdgeIpLocation(BaseAPIModel):
    """
    Model representing the location information of an edge IP.
    """

    as_number: Optional[int] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    region_code: Optional[str] = None


class IpType(BaseAPIModel):
    """
    Model representing an IP address with its location.
    """

    ip: Optional[str] = None
    location: EdgeIpLocation = Field(default_factory=EdgeIpLocation, alias="ipLocation")


class BaseResponse(BaseAPIModel):
    """
    Base model that contains common fields present in all Akamai's API responses.
    """

    completed_time: str
    created_by: str
    created_time: str
    edge_ip_location: EdgeIpLocation = Field(default_factory=EdgeIpLocation)
    execution_status: str
