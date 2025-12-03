#!/usr/bin/env python3

"""
Main entry point for the CLI application.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated

from .__version__ import __epilog__, __version__
from .api import AkamaiAPI
from .cache import Cache
from .commands import app as commands_app
from .config import MAX_REQUEST_TIMEOUT, MIN_REQUEST_TIMEOUT, Config, init_config_file
from .exceptions import handle_exceptions

_HELP_PANEL_AUTH = "Authentication Options"
_HELP_PANEL_CACHE = "Cache Options"
_HELP_PANEL_NETWORK = "Network Options"

app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True, epilog=__epilog__)
console = Console()
console_stderr = Console(stderr=True)
config = Config().main


@dataclass
class _AppContext:
    """
    Dataclass object that contains all the instances needed for the subcommands.
    """

    api: AkamaiAPI
    console: Console
    console_stderr: Console


def _version_callback(value: Optional[bool], ctx: typer.Context) -> None:
    """
    Callback function to show the program's version and exit.
    """
    if value:
        console.print(f"{ctx.info_name} {__version__}", highlight=False)
        raise typer.Exit()


@app.callback()
@handle_exceptions(console_stderr)
def main(
    ctx: typer.Context,
    edgerc: Annotated[
        Path,
        typer.Option(
            help="Path to EdgeGrid authentication file.",
            rich_help_panel=_HELP_PANEL_AUTH,
            exists=True,
            file_okay=True,
        ),
    ] = config.edgerc_path,
    section: Annotated[
        str,
        typer.Option(
            help="Section in EdgeGrid file to use.",
            rich_help_panel=_HELP_PANEL_AUTH,
        ),
    ] = config.edgerc_section,
    cache_dir: Annotated[
        Path,
        typer.Option(
            help="Use a custom cache directory.",
            rich_help_panel=_HELP_PANEL_CACHE,
            exists=True,
            dir_okay=True,
        ),
    ] = config.cache_dir,
    cache_ttl: Annotated[
        float,
        typer.Option(help="Set a custom cache TTL.", rich_help_panel=_HELP_PANEL_CACHE),
    ] = config.cache_ttl,
    use_cache: Annotated[
        bool,
        typer.Option(
            help="Use cache to improve performace.", rich_help_panel=_HELP_PANEL_CACHE
        ),
    ] = config.use_cache,
    proxy: Annotated[
        Optional[str],
        typer.Option(
            help="Use a proxy server for requests.", rich_help_panel=_HELP_PANEL_NETWORK
        ),
    ] = config.proxy,
    request_timeout: Annotated[
        int,
        typer.Option(
            help="Set custom timeout for requests.",
            rich_help_panel=_HELP_PANEL_NETWORK,
            min=MIN_REQUEST_TIMEOUT,
            max=MAX_REQUEST_TIMEOUT,
        ),
    ] = config.request_timeout,
    validate_certs: Annotated[
        bool,
        typer.Option(
            help="Enable SSL certificate validation for HTTPS requests.",
            rich_help_panel=_HELP_PANEL_NETWORK,
        ),
    ] = config.validate_certs,
    init_config_file: Annotated[
        Optional[bool],
        typer.Option(
            "--init-config-file",  # TODO: Make --init-config-file a subcommand (?)
            help="Generate configuration file with default values and exit.",
            callback=lambda value: init_config_file(value, console),
            is_eager=True,
        ),
    ] = None,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="Show program version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """
    Command-line interface to make requests to Akamai API.
    """
    cache = Cache(cache_dir=cache_dir, ttl=cache_ttl, use_cache=use_cache)

    api = AkamaiAPI(
        edgerc=edgerc,
        section=section,
        timeout=request_timeout,
        cache=cache,
        proxy=proxy,
        verify=validate_certs,
    )

    # Pass initialized instances to subcommands using context object
    # to avoid intializing them in each subcommand.
    ctx.obj = _AppContext(api=api, console=console, console_stderr=console_stderr)


app.add_typer(commands_app)


if __name__ == "__main__":
    app()
