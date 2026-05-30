#!/usr/bin/env python3

"""
Get a network list's most recent Sync Point version.
"""

import warnings

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from typing_extensions import Annotated

from akcli.api import AkamaiAPI
from akcli.commands._common import common_args, handle_get_field
from akcli.config import Config
from akcli.exceptions import NoRecordsFound, handle_exceptions
from akcli.models.nl_response import NetworkList
from akcli.utils import print_json

from ._common import print_nl_table

_COMMAND_NAME = "get"

app = typer.Typer()
config = Config().nl.get


def _print_nl_elements(console: Console, nl: NetworkList) -> None:
    """
    Print the elements of a Network List in a multi-column layout.
    """
    elements = nl.list or []
    title = f"\n[b]Network List Elements ({len(elements)}):[/b]"

    if not elements:
        warnings.warn(f"No elements found for NL '{nl.unique_id}'.", NoRecordsFound, stacklevel=2)
        return

    # Create a `Columns` item to use all the terminal width and wrap it into a `Panel`
    cols = Columns(elements, equal=True, expand=True)
    panel = Panel.fit(cols, title=title, border_style="magenta")
    console.print(panel)


@app.command(name=_COMMAND_NAME)
@handle_exceptions()
@common_args
def nl_get(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="ID of the Network List.")],
    include_elements: Annotated[
        bool, typer.Option(help="If enabled, the response include all the elements of each NL.")
    ] = config.include_elements,
    extended: Annotated[
        bool,
        typer.Option(
            help="Provide additional information, such as who created the NL or network the status (Prod or Staging)."
        ),
    ] = config.extended,
) -> None:
    """
    Get a network list's most recent Sync Point version.
    """
    api: AkamaiAPI = ctx.obj.api
    console = ctx.obj.console

    nl = api.nl_get(id, include_elements, extended)

    handle_get_field(console, ctx, nl)

    # Warn and exit program if no records found
    if nl is None:
        warnings.warn("No records found", NoRecordsFound, stacklevel=2)
        raise typer.Exit()

    if ctx.params.get("json"):
        print_json(console, nl.model_dump(by_alias=True))
        raise typer.Exit()

    # Pass a [nl] since `print_nl_table()` expect a list
    print_nl_table(console, [nl], extended)

    if include_elements:
        _print_nl_elements(console, nl)
