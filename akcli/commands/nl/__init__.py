#!/usr/bin/env python3

"""
Tool to manage Akamai Network Lists.
"""

import typer

from .get import app as get_app
from .list import app as list_app

_COMMAND_NAME = "nl"
_COMMAND_HELP = "Manage Akamai Network Lists."

app = typer.Typer(name=_COMMAND_NAME, help=_COMMAND_HELP, no_args_is_help=True)

app.add_typer(list_app)
app.add_typer(get_app)
