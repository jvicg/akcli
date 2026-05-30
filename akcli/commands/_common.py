#!/usr/bin/env python3

"""
Common command arguments and options.
"""

import warnings
from functools import reduce
from typing import Any, Dict, Optional

import typer
from merge_args import merge_args
from rich.console import Console
from typing_extensions import Annotated

from akcli.exceptions import NoRecordsFound
from akcli.models import BaseAPIModel
from akcli.typing import GenericFunction
from akcli.utils import print_json


def _get_field(field: str, data: Dict) -> Any:
    """
    Navigate a nested dict using dot notation and return the value at the given path.
    Returns None if any key in the path does not exist or the value is not a dict.
    """
    return reduce(lambda d, k: d.get(k) if isinstance(d, dict) else None, field.split("."), data)


def handle_get_field(console: Console, ctx: typer.Context, response: BaseAPIModel) -> None:
    """
    Handle the `--get-field` flag by navigating the response and printing the value.
    Prints the value directly if it is a simple type, or as JSON if it is a complex type, and exits the program.
    """
    if get_field := ctx.params.get("get_field"):
        value = _get_field(get_field, response.model_dump(by_alias=True))

        if value is None:
            warnings.warn(f"Field '[b]{get_field}[/b]' not found in the response.", NoRecordsFound, stacklevel=2)
            raise typer.Exit()

        if isinstance(value, (str, int, float, bool)):
            console.print(value)
        else:
            print_json(console, value)

        raise typer.Exit()


def common_args(
    func: GenericFunction,
) -> GenericFunction:
    """
    Decorator to add common arguments to multiple commands.
    Source: https://github.com/fastapi/typer/issues/296
    """

    @merge_args(func)
    def wrapper(
        ctx: typer.Context,
        json: Annotated[bool, typer.Option(help="Print output in JSON format.")] = False,
        get_field: Annotated[Optional[str], typer.Option(help="Get a specific field of the JSON API response.")] = None,
        **kwargs,
    ) -> None:
        return func(ctx=ctx, **kwargs)

    return wrapper  # type: ignore
