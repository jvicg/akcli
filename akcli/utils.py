#!/usr/bin/env python3

"""
Helper functions used across the project.
"""

from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .typing import ColumnHeaders, JSONResponse, PanelType


def snakecase_to_camel(s: str) -> str:
    """Convert a snake case string to camel case."""
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def snakecase_to_title(s: str) -> str:
    """
    Convert snake case string to titled string.
    i.e: "example_name" -> "Example Name"
    """
    return s.replace("_", " ").title()


def _print_panel(console: Console, msg: str, panel_type: PanelType) -> None:
    """
    Generic function to print a rich.Panel with a given type. The type determines the style of the panel.
    """
    styles = {
        "info": ("Info", "white"),
        "error": ("[red]Error[/red]", "red"),
        "warning": ("[yellow]Warning[/yellow]", "yellow"),
        "result": ("[blue]Result[/blue]", "blue"),
    }

    if panel_type not in styles:
        raise ValueError(f"Invalid panel type: {panel_type}")

    title, border_style = styles[panel_type]
    console.print(
        Panel.fit(msg, title=title, border_style=border_style, title_align="left")
    )


def print_info(console: Console, msg: str) -> None:
    """
    Print info in pretty format using rich.Panel.
    """
    _print_panel(console, msg, panel_type="info")


def print_error(console: Console, msg: str) -> None:
    """
    Print error in pretty format using rich.Panel.
    """
    _print_panel(console, msg, panel_type="error")


def print_warning(console: Console, msg: str) -> None:
    """
    Print a warning in pretty format using rich.Panel.
    """
    _print_panel(console, msg, panel_type="warning")


def print_result(console: Console, msg: str) -> None:
    """
    Print a result in pretty format using rich.Panel.
    """
    _print_panel(console, msg, panel_type="result")


def print_json(console: Console, data: JSONResponse) -> None:
    """
    Print data as pretty JSON to the console.
    """
    import json

    pretty_json = json.dumps(data, indent=4, default=str)
    console.print(pretty_json, highlight=True)


def create_table(
    title: Optional[str] = None,
    show_header: bool = True,
    show_lines: bool = False,
    expand: bool = True,
    header_style: str = "bright_black",
    title_style: str = "bold yellow",
    caption: Optional[str] = None,
    border_style: str = "bright_black",
    box_style: box.Box = box.ROUNDED,
    columns: Optional[ColumnHeaders] = None,
) -> Table:
    """
    Create a Table with the given parameters. The columns must be passed as a list of dictionaries
    that contain the parameters needed to build the Table headers.

    Each dictionary in the list will define a column.
    """
    table = Table(
        title=title,
        show_header=show_header,
        show_lines=show_lines,
        expand=expand,
        header_style=header_style,
        title_style=title_style,
        caption=caption,
        border_style=border_style,
        box=box_style,
    )

    for column in columns or []:
        table.add_column(**column)

    return table


def highlight(text: str, style: str = "bold underline yellow") -> str:
    """
    Highlight text with the given style.
    """
    return f"[{style}]{text}[/{style}]"
