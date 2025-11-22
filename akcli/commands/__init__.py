#!/usr/bin/env python3

"""
CLI subcommands.
"""

import typer

from .dig import app as dig_app
from .translate import app as translate_app

app = typer.Typer()

app.add_typer(dig_app)
app.add_typer(translate_app)
