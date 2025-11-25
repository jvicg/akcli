#!/usr/bin/env python3

"""
Command-line interface to make requests to Akamai API.
"""

import warnings

from rich.console import Console

from .utils import print_warning

"""
NOTE: This custom warning handler is configured at top level to ensure 
that the handler is active before any imported module can emit warnings.
"""


def _warning_handler(message, category, filename, lineno, file=None, line=None) -> None:
    """
    Custom warning handler to print warnings to stderr using `rich`.
    """
    _console = Console(stderr=True)
    print_warning(_console, f"{category.__name__}: {message}")


warnings.showwarning = _warning_handler
