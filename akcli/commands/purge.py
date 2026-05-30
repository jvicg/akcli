#!/usr/bin/env python3

"""
Tool to purge an object or list of objects on the Akamai Network.
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from akcli.config import Config
from akcli.exceptions import InvalidParams, MutuallyExclusiveArgs, handle_exceptions
from akcli.utils import print_json, print_success

from ._common import common_args, handle_get_field

_COMMAND_NAME = "purge"

app = typer.Typer()
config = Config().purge


class _PurgeMethod(str, Enum):
    """
    Supported purge methods.
    """

    invalidate = "invalidate"
    delete = "delete"


class _PurgeNetwork(str, Enum):
    """
    Supported networks.
    """

    staging = "staging"
    production = "production"


class _PurgeType(str, Enum):
    """
    Supported purge types.
    """

    tag = "tag"
    url = "url"
    cpcode = "cpcode"


def _validate_urls(urls: List[str]) -> None:
    """Ensure that URLs start with http:// or https://"""
    for u in urls:
        if not u.startswith(("http://", "https://")):
            raise InvalidParams(
                f"Invalid URL [b]'{u}[/b]'. URLs/ARLs must include the protocol scheme (http:// or https://)."
            )


def _file_to_list(f: Path) -> List[str]:
    """Parse the non-empty lines of a file into a list, stripping whitespace."""
    return [obj.strip() for obj in f.read_text().splitlines() if obj.strip()]


@app.command(name=_COMMAND_NAME)
@handle_exceptions()
@common_args
def purge(
    ctx: typer.Context,
    objects: Annotated[
        Optional[List[str]], typer.Argument(help="List with the objects to purge (CP codes, tags or URLs/ARLs).")
    ] = None,
    from_file: Annotated[
        Optional[Path], typer.Option(help="Path to a file with one object per line.", exists=True, file_okay=True)
    ] = None,
    method: Annotated[_PurgeMethod, typer.Option(help="Method used to purge.")] = config.method,  # type: ignore
    network: Annotated[_PurgeNetwork, typer.Option(help="Akamai network.")] = config.network,  # type: ignore
    purge_type: Annotated[_PurgeType, typer.Option(help="The type of objects to purge.")] = config.type,  # type: ignore
) -> None:
    """
    Tool to purge an object or list of objects on the Akamai Network.
    """
    api = ctx.obj.api
    console = ctx.obj.console

    # Validate args
    if objects and from_file:
        raise MutuallyExclusiveArgs("'--from-file' and positional arguments are mutually exclusive.")

    if not objects and not from_file:
        raise InvalidParams("Provide either objects as positional arguments or use '--from-file'.")

    if from_file is not None:
        objects = _file_to_list(from_file)

    # Raise error if URLs/ARLs don't start with 'http://' or 'https://'
    if purge_type == _PurgeType.url:
        _validate_urls(objects)  # type: ignore

    response = api.purge(method, network, purge_type, objects)
    handle_get_field(console, ctx, response)

    if ctx.params.get("json"):
        print_json(console, response.model_dump(by_alias=True))
        raise typer.Exit()

    msg = (
        f"Your request will be completed in [b]{response.estimated_seconds}[/b] seconds.\n"
        f"Purge ID: [u]{response.purge_id}[/u]"
    )

    print_success(console, msg)
