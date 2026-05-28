#!/usr/bin/env python3

"""
Common command arguments and options.
"""

import typer
from merge_args import merge_args
from typing_extensions import Annotated

from akcli.typing import GenericFunction


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
        **kwargs,
    ) -> None:
        return func(ctx=ctx, **kwargs)

    return wrapper  # type: ignore
