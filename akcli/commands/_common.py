#!/usr/bin/env python3

"""
Common command arguments and options.
"""

from typing import Optional

import typer
from merge_args import merge_args
from typing_extensions import Annotated

from ..typing import GenericFunction


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
        json: Annotated[
            Optional[bool], typer.Option("--json", help="Output in JSON format.")
        ] = None,
        csv: Annotated[
            Optional[bool], typer.Option("--csv", help="Output in CSV format.")
        ] = None,
        **kwargs,
    ) -> None:
        return func(ctx=ctx, **kwargs)

    return wrapper  # type: ignore
