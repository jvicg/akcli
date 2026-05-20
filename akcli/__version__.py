#!/usr/bin/env python3

"""
Package metadata.
"""

from importlib.metadata import PackageNotFoundError, metadata

try:
    m = metadata("akcli")
    __title__ = m["Name"]
    __version__ = m["Version"]
    __description__ = m["Summary"]
    __url__ = m.get_all("Project-Url", "")[1].split(", ")[1]
    __author__ = m["Author"]
    __author_email__ = m["Author-email"]
    __license__ = m["License"]

# Handle cases when package is not installed (i.e running with `python -m akcli.main`)
except (PackageNotFoundError, KeyError):
    __title__ = "akcli"
    __version__ = "0.0.0-dev"
    __description__ = "Command-line interface to make requests to Akamai API."
    __url__ = f"https://github.com/jvicg/{__title__}"
    __author__ = "Javier Correa Guerrero"
    __author_email__ = "jcorreag@pm.me"
    __license__ = "MIT"

__epilog__ = f"See documentation at: [u]{__url__}[/u] for more information."  # NOTE: Epilog is not being used atm
