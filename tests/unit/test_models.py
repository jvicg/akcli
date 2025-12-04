#!/usr/bin/env python3

"""
Suite of tests for `BaseAPIModel` class.
"""

from typing import Optional

import pytest

from akcli.exceptions import InvalidResponse
from akcli.models._base import BaseAPIModel, IpType

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def valid_data():
    """
    Valid data with camelCase keys for testing.
    """
    return {
        "dummyValue": "test",
        "neededValue": 42,
    }


@pytest.fixture
def dummy_model():
    """
    Dummy model class to test BaseAPIModel methods.
    """

    class DummyModel(BaseAPIModel):
        dummy_value: Optional[str] = None
        needed_value: int
        unused_value: Optional[float] = None

    return DummyModel


# ----------------------
# Tests
# ----------------------


def test_initialization_with_valid_data(dummy_model, valid_data):
    """
    Test that key conversion from camelCase to snake_case works correctly and default values are set if field is missing.
    """
    model = dummy_model.parse_model(valid_data)

    assert model.dummy_value == "test"
    assert model.needed_value == 42
    assert model.unused_value is None


def test_initialization_with_missing_required_field(dummy_model):
    """
    Test initialization of BaseAPIModel subclass with missing required field raises InvalidResponse.
    """
    invalid_data = {
        "dummyValue": "test",
    }

    with pytest.raises(InvalidResponse):
        dummy_model.parse_model(invalid_data)


def test_initialization_with_invalid_field_type(dummy_model):
    """
    Test initialization of BaseAPIModel subclass with invalid field type raises InvalidResponse.
    """
    invalid_data = {
        "dummyValue": "test",
        "neededValue": "not an integer",
    }

    with pytest.raises(InvalidResponse):
        dummy_model.parse_model(invalid_data)


def test_none_optional_field(dummy_model, valid_data):
    """
    Test that optional fields can be set to None without raising exceptions.
    """
    valid_data["dummyValue"] = None
    model = dummy_model.parse_model(valid_data)
    assert model.dummy_value is None


def test_extra_fields_are_ignored(dummy_model, valid_data):
    """
    Test that extra fields in the input data are ignored during model initialization.
    """
    data_with_extra = valid_data.copy()
    data_with_extra["extraField"] = "should be ignored"

    model = dummy_model.parse_model(data_with_extra)
    dumped = model.model_dump()

    assert not hasattr(model, "extra_field")
    assert "extra_field" not in dumped


def test_dump_uses_camel_case(dummy_model, valid_data):
    """
    Test that model_dump with by_alias=True returns keys in camelCase.
    """
    model = dummy_model.parse_model(valid_data)
    dumped = model.model_dump(by_alias=True)

    assert "dummyValue" in dumped
    assert "neededValue" in dumped


def test_nested_model_parsing():
    """
    Test parsing of nested models with camelCase keys.
    """
    data = {
        "ip": "1.1.1.1",
        "ipLocation": {
            "countryCode": "US",
            "city": "NYC",
        },
    }

    model = IpType.parse_model(data)
    assert model.location.country_code == "US"
    assert model.location.city == "NYC"
