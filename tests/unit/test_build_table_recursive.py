#!/usr/bin/env python3

"""
Unit tests for the `_build_table_recursive` function in the `translate` subcommand.

This function recursively builds a Rich table from a dictionary, creating subtables
for nested dictionaries. These tests verify the table structure and cell content
for different input types without invoking the CLI or the HTTP server.
"""

import pytest
from rich.table import Table

from akcli.commands.translate import _TABLE_PARAMS, _build_table_recursive
from akcli.utils import create_table

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def table():
    """Empty table to use as the main table in tests."""
    return create_table(**_TABLE_PARAMS)


# ----------------------
# Helpers
# ----------------------


def get_cell(table: Table, row: int, col: int):
    """
    Helper to get the rendered content of a cell by row and column index.
    """
    return table.columns[col]._cells[row]


def get_subtable(table: Table, row: int):
    """
    Helper to get the subtable stored in the second column of a given row.
    """
    cell = get_cell(table, row, col=1)
    assert isinstance(cell, Table), f"Expected a Table in row {row}, got {type(cell)}"
    return cell


# ----------------------
# Tests
# ----------------------


def test_none_input_adds_no_rows(table):
    """
    Test that passing None as obj does not add any rows to the table.
    """
    _build_table_recursive(table, None, title="Some Title")
    assert len(table.rows) == 0


def test_simple_string_adds_one_row(table):
    """
    Test that a simple string value adds a single row with the title and value.
    """
    _build_table_recursive(table, "hello", title="My Field")

    assert len(table.rows) == 1
    assert get_cell(table, row=0, col=0) == "My Field"
    assert get_cell(table, row=0, col=1) == "hello"


def test_simple_int_adds_one_row(table):
    """
    Test that a simple integer value is coerced to string and added as a row.
    """
    _build_table_recursive(table, 42, title="Count")

    assert len(table.rows) == 1
    assert get_cell(table, row=0, col=0) == "Count"
    assert get_cell(table, row=0, col=1) == "42"


def test_flat_dict_adds_rows_for_each_key(table):
    """
    Test that a flat dictionary adds one row per key to the table,
    with keys formatted as title case.
    """
    obj = {"first_name": "John", "last_name": "Doe"}
    _build_table_recursive(table, obj)

    assert len(table.rows) == 2
    assert get_cell(table, row=0, col=0) == "First Name"
    assert get_cell(table, row=0, col=1) == "John"
    assert get_cell(table, row=1, col=0) == "Last Name"
    assert get_cell(table, row=1, col=1) == "Doe"


def test_nested_dict_creates_subtable(table):
    """
    Test that a nested dictionary creates a subtable in the second column.
    """
    obj = {"address": {"city": "Granada", "country": "Spain"}}
    _build_table_recursive(table, obj)

    assert len(table.rows) == 1
    assert get_cell(table, row=0, col=0) == "Address"

    subtable = get_subtable(table, row=0)
    assert len(subtable.rows) == 2
    assert get_cell(subtable, row=0, col=0) == "City"
    assert get_cell(subtable, row=0, col=1) == "Granada"
    assert get_cell(subtable, row=1, col=0) == "Country"
    assert get_cell(subtable, row=1, col=1) == "Spain"


def test_deeply_nested_dict_creates_nested_subtables(table):
    """
    Test that deeply nested dictionaries produce nested subtables recursively.
    """
    obj = {"level_one": {"level_two": {"value": "deep"}}}
    _build_table_recursive(table, obj)

    assert len(table.rows) == 1
    subtable_l1 = get_subtable(table, row=0)

    assert len(subtable_l1.rows) == 1
    subtable_l2 = get_subtable(subtable_l1, row=0)

    assert len(subtable_l2.rows) == 1
    assert get_cell(subtable_l2, row=0, col=0) == "Value"
    assert get_cell(subtable_l2, row=0, col=1) == "deep"


def test_none_value_in_dict_adds_no_row(table):
    """
    Test that a None value inside a dictionary does not add a row.
    """
    obj = {"present": "yes", "missing": None}
    _build_table_recursive(table, obj)

    assert len(table.rows) == 1
    assert get_cell(table, row=0, col=0) == "Present"
    assert get_cell(table, row=0, col=1) == "yes"


def test_mixed_dict_with_nested_and_simple_values(table):
    """
    Test a dictionary with both simple values and nested dictionaries.
    """
    obj = {
        "status": "active",
        "details": {"code": "200", "message": "OK"},
    }
    _build_table_recursive(table, obj)

    assert len(table.rows) == 2
    assert get_cell(table, row=0, col=0) == "Status"
    assert get_cell(table, row=0, col=1) == "active"
    assert get_cell(table, row=1, col=0) == "Details"

    subtable = get_subtable(table, row=1)
    assert len(subtable.rows) == 2
    assert get_cell(subtable, row=0, col=0) == "Code"
    assert get_cell(subtable, row=0, col=1) == "200"
