#!/usr/bin/env python3

"""
List all Network Lists available for the authenticated user.
"""

import warnings
from enum import Enum
from typing import Optional

import typer
from typing_extensions import Annotated

from akcli.api import AkamaiAPI
from akcli.commands._common import common_args, handle_get_field
from akcli.commands.nl._common import print_nl_table
from akcli.config import Config
from akcli.exceptions import NoRecordsFound, handle_exceptions
from akcli.utils import highlight, print_info, print_json

_COMMAND_NAME = "list"


app = typer.Typer()
config = Config().nl.list


class _ListType(str, Enum):
    """
    Supported list types.
    """

    ip = "ip"
    geo = "geo"


def _parse_ip_type(v: str) -> str:
    """Return `list_type` user input in upper case."""
    return v.upper()


@app.command(name=_COMMAND_NAME)
@handle_exceptions()
@common_args
def nl_list(
    ctx: typer.Context,
    list_type: Annotated[
        _ListType, typer.Option(help="Filter to lists of only the given type.", callback=_parse_ip_type)
    ] = config.list_type,  # type: ignore
    search: Annotated[
        Optional[str], typer.Option(help="Only list items that match the specified string.")
    ] = config.search,  # type: ignore
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
    List all Network Lists available for the authenticated user.
    """
    api: AkamaiAPI = ctx.obj.api
    console = ctx.obj.console

    # Make user to confirm action and make them know a better way to get single NL elements
    if include_elements:
        print_info(
            console,
            f"Consider using {highlight('akcli nl get <id> --include-elements')} "
            "to inspect a single Network List with its elements.",
        )
        typer.confirm("This may return a large amount of data. Do you want to continue?", abort=True)

    response = api.nl_list(list_type, search, include_elements, extended)  # type: ignore
    handle_get_field(console, ctx, response)

    nls = response.network_lists

    # Warn and exit program if no records found
    if nls is None:
        warnings.warn("No records found", NoRecordsFound, stacklevel=2)
        raise typer.Exit()

    # If include_elements is True, print raw json to avoid an unreadble table with thousands of IPs
    if ctx.params.get("json") or include_elements:
        print_json(console, response.model_dump(by_alias=True))
        raise typer.Exit()

    print_nl_table(console, nls, extended)
