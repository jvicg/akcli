#!/usr/bin/env python3

"""
Tool to resolve domains FQDNs using Akamai Edge Diagnostics API.
"""

import warnings
from enum import Enum

import typer
from typing_extensions import Annotated

from ..config import Config
from ..exceptions import DigNoAnswerWarning, handle_exceptions
from ..utils import create_table, highlight, print_json
from ._common import common_args

_COMMAND_NAME = "dig"

_COLUMNS_HEADERS = [
    {"header": "Hostname"},
    {"header": "TTL", "justify": "right"},
    {"header": "Class", "justify": "center"},
    {"header": "Type", "justify": "center"},
    {"header": "Value", "style": "bold magenta"},
]

_COLUMNS_HEADERS_SHORT = [
    {"header": "Value", "style": "magenta"},
]

app = typer.Typer()
config = Config().dig


class _DNSType(str, Enum):
    """
    Supported DNS record types for Akamai Edge Diagnostics queries.
    """

    A = "A"
    AAAA = "AAAA"
    SOA = "SOA"
    CNAME = "CNAME"
    PTR = "PTR"
    NS = "NS"
    TXT = "TXT"
    MX = "MX"
    SRV = "SRV"
    CAA = "CAA"
    ANY = "ANY"


@app.command(name=_COMMAND_NAME)
@handle_exceptions()
@common_args
def dig(
    ctx: typer.Context,
    hostname: Annotated[str, typer.Argument(help="Hostname to query.")],
    query_type: Annotated[
        _DNSType, typer.Option(help="Choose type of query.")
    ] = config.query_type,  # type: ignore
    short: Annotated[
        bool, typer.Option(help="Show only returned values.")
    ] = config.short_output,
) -> None:
    """
    Tool to resolve domains FQDNs using Akamai Edge Diagnostics API.
    """
    api = ctx.obj.api
    console = ctx.obj.console

    response = api.dig(hostname, query_type)
    answer_section = response.result.answer_section

    if not answer_section:
        warnings.warn(
            f"No register matches the query: {highlight(hostname)}", DigNoAnswerWarning
        )
        raise typer.Exit()

    if ctx.params.get("json"):
        print_json(console, response.model_dump())
        raise typer.Exit()

    table = create_table(
        columns=_COLUMNS_HEADERS_SHORT if short else _COLUMNS_HEADERS,
        caption=f"Result of query: {query_type.value} {hostname}",
    )

    for item in answer_section:
        if short:
            row = (item.value,)
        else:
            row = (
                item.hostname,
                str(item.ttl),
                item.record_class,
                item.record_type,
                item.value,
            )
        table.add_row(*row)

    console.print(table, new_line_start=True)
