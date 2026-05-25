#!/usr/bin/env python3

"""
Configuration file for the Sphinx documentation builder.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))  # noqa: PTH100

from akcli.__version__ import __author__, __title__, __version__

# ----------------------
# Project metadata
# ----------------------

project = __title__
author = __author__
version = __version__
release = __version__
copyright = f"2026, {__author__}"

# ----------------------
# HTML output
# ----------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "navigation_depth": 3,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
    "display_version": True,
}

html_show_sourcelink = False
html_show_sphinx = False
html_copy_source = False
html_last_updated_fmt = "%Y-%m-%d"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
