#!/usr/bin/env python3

"""
Common variables and functions of the `nl` comnand.
"""

from typing import List, Tuple

from rich.console import Console

from akcli.models.nl_response import NetworkList
from akcli.utils import create_table

_NL_HEADERS = [
    {"header": "id"},
    {"header": "name", "justify": "center"},
    {"header": "description", "justify": "center"},
    {"header": "type", "justify": "center"},
    {"header": "element_count", "justify": "center"},
]

_NL_HEADERS_EXTENDED = [
    *_NL_HEADERS,
    {"header": "staging_status", "justify": "center", "style": "bold magenta"},
    {"header": "production_status", "justify": "center", "style": "bold magenta"},
    {"header": "created_by", "justify": "center", "style": "bold magenta"},
    {"header": "updated_by", "justify": "center", "style": "bold magenta"},
]


def _nl_to_row(nl: NetworkList, extended: bool) -> Tuple:
    """
    Build a row with base or extended values depending on `extended`.
    """
    base = (
        nl.unique_id,
        nl.name,
        nl.description,
        nl.type,
        str(nl.element_count),
    )
    if not extended:
        return base

    return (*base, nl.staging_activation_status, nl.production_activation_status, nl.created_by, nl.updated_by)


def print_nl_table(console: Console, nls: List[NetworkList], extended: bool) -> None:
    """
    Create and print a Network List table. It can print a multpile or single NL.
    """
    table = create_table(columns=_NL_HEADERS_EXTENDED if extended else _NL_HEADERS, show_lines=True)

    for nl in nls:
        table.add_row(*_nl_to_row(nl, extended))

    console.print(table, new_line_start=True)
