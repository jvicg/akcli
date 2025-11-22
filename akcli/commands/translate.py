#!/usr/bin/env python3

"""
Tool to translate Akamai Error References.
"""

from typing import Any, Optional

import typer
from rich.table import Table
from typing_extensions import Annotated

from ..config import Config
from ..exceptions import handle_exceptions
from ..typing import TableParams
from ..utils import (
    create_table,
    highlight,
    print_json,
    print_warning,
    snakecase_to_title,
)
from ._common import common_args

_COMMAND_NAME = "translate"

_COLUMNS_HEADERS = [
    {"style": "bold white"},
    {"style": "white"},
]

_TABLE_PARAMS: TableParams = {
    "show_header": False,
    "show_lines": True,
    "columns": _COLUMNS_HEADERS,
}

_EXCLUDED_FIELDS = {"log_lines"}
"""Fields of `TranslateReponse.result` that won't be printed to stdout."""

app = typer.Typer()
config = Config().translate


def _build_table_recursive(table: Table, obj: Any, title: Optional[str] = None) -> None:
    """
    Recursively create subsections and append them to the main `table` till `obj` is not a dict,
    for each dictionary a subtable will be created.
    """
    if obj is None:
        return

    # Simple value: add a row
    if not isinstance(obj, dict):
        table.add_row(title, str(obj))
        return

    subtable = create_table(**_TABLE_PARAMS)

    for key, value in obj.items():
        formatted_key = snakecase_to_title(key)
        # If title is None, we're in first level, so pass table instead of subtable
        _build_table_recursive(
            table if title is None else subtable, value, formatted_key
        )

    if title is not None:
        table.add_row(title, subtable)


@app.command(name=_COMMAND_NAME)
@handle_exceptions()
@common_args
def translate(
    ctx: typer.Context,
    id: Annotated[
        str,
        typer.Argument(help="Reference ID of the error."),
    ],
    trace: Annotated[
        bool,
        typer.Option(
            help="Get logs from all edge servers involved to process in serving the request."
        ),
    ] = config.trace,
) -> None:
    """
    Tool to translate Akamai Error References.
    """
    api = ctx.obj.api
    console = ctx.obj.console

    response = api.translate(id, trace)
    result = response.result

    if result.no_logs:
        print_warning(
            console,
            f"Not found any logs that matches the Reference ID: {highlight(id)}",
        )
        raise typer.Exit()

    if ctx.params.get("json"):
        print_json(console, response.model_dump())
        raise typer.Exit()

    table = create_table(
        **_TABLE_PARAMS,
        caption=f"Logs for Reference ID: {id}",  # Add caption to the main table
    )

    serialized_result = result.model_dump(exclude=_EXCLUDED_FIELDS, mode="python")
    # Recursively add all result fields as rows/subtables
    _build_table_recursive(table, serialized_result)

    console.print(table, new_line_start=True)
