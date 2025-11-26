#!/usr/bin/env python3

"""
Custom exception classes used across the project.
"""

from functools import wraps
from typing import Any, Callable, Optional

import typer
from rich.console import Console
from typer import Exit

from .typing import GenericFunction
from .utils import print_error

ERR_UNEXPECTED = -1
ERR_KEYBOARD_INTERRUPT = 130


# ----------------------
# Exceptions
# ----------------------


class _BaseException(Exception):
    """
    Private base class to build all application-specific exceptions.

    Provides a standard message and exit code for controlled termination
    of the CLI program when an expected error occurs and a method to exit gracefully.

    All subclasses should define `exit_code` and `default_msg` class attributes.
    """

    exit_code = 99
    default_msg = "An error occurred"

    def __init__(self, msg: Optional[str] = None) -> None:
        _exception_name = type(self).__name__

        self.msg = (
            f"{_exception_name}: {msg}"
            if msg
            else getattr(  # Set default message if none provided
                self, "default_msg", f"{_exception_name}: {type(self).default_msg}"
            )
        )
        super().__init__(self.msg)

    def __repr__(self) -> str:
        """
        String representation of the exception.
        """
        return f"[{self.__class__.__name__}] {self.msg}"

    def exit(self) -> None:
        """
        Gracefully terminate the program using the exception's `exit_code`.
        """
        raise Exit(code=self.exit_code)


class HandledException(_BaseException):
    """
    Base class to build all handled exceptions in the application.

    This class inherits all behavior from `_BaseException`, but exists only
    to provide a clean and conventional name to catch in application code.
    """

    pass


class ResourceNotFound(HandledException):
    """Raised when a resource is not found in the API."""

    exit_code = 11
    default_msg = "The requested resource could not be found."


class InvalidCredentials(HandledException):
    """Raised when API returns either 403 or 401."""

    exit_code = 12
    default_msg = "Invalid API credentials or unauthorized access."


class InvalidResponse(HandledException):
    """Raised when the API response cannot be parsed."""

    exit_code = 13
    default_msg = "Received an invalid or unexpected API response."


class RequestTimeout(HandledException):
    """Raised when a request to the API times out."""

    exit_code = 14
    default_msg = "The request to the API timed out."


class RequestError(HandledException):
    """Raised when requests raised a non-handled exception."""

    exit_code = 15
    default_msg = "An unexpected error occurred during the API request."


class MethodNotAllowed(HandledException):
    """Raised when the HTTP method is not allowed for the endpoint."""

    exit_code = 16
    default_msg = "The HTTP method is not allowed for this endpoint."


class TooManyRequests(HandledException):
    """Raised when the API rate limits the client."""

    exit_code = 17
    default_msg = "Too many requests: the API rate limit has been reached."


class ProxyError(HandledException):
    """Raised when a proxy error occurs during a request."""

    exit_code = 18
    default_msg = "A proxy error occurred while connecting to the API."


class BadRequest(HandledException):
    """Raised when the API returns a bad request response."""

    exit_code = 19
    default_msg = "The API request was malformed or invalid."


class MaxAttempsExceeded(HandledException):
    """Raised when the try to poll API more times than the limit established."""

    exit_code = 20
    default_msg = "Excedeed the max polling attemps."


class InvalidEdgeRcSection(HandledException):
    """Raised when the .edgerc section is invalid or not found."""

    exit_code = 70
    default_msg = "The specified .edgerc section is invalid or missing."


class InvalidPanelType(HandledException):
    """Raised when an invalid panel type is used."""

    exit_code = 61
    default_msg = "Invalid panel type specified."


# ----------------------
# Warnings
# ----------------------


class _BaseWarning(UserWarning):
    """
    Private base class to build all application-specific warnings.
    """

    pass


class InvalidConfigSectionWarning(_BaseWarning):
    """Warning raised when a section in config file is invalid."""

    pass


class InvalidOptionWarning(_BaseWarning):
    """Warning raised when the configuration cannot be parsed."""

    pass


class FileUnableToParseWarning(_BaseWarning):
    """Warning raised when the configuration cannot be parsed."""

    pass


class UnableToGenerateConfigWarning(_BaseWarning):
    """Warning raised when unable to generate the config file."""

    pass


class DigNoAnswerWarning(_BaseWarning):
    """Warning raised when dig command returns no answer."""

    pass


class TranslateNoLogsWarning(_BaseWarning):
    """Warning raised when translate command finds no logs for a given Reference ID."""

    pass


# ----------------------
# Handlers
# ----------------------


def handle_exceptions(
    console: Optional[Console] = None,
) -> Callable[[GenericFunction], GenericFunction]:
    """
    Decorator to handle the common exceptions. It will obtain console from `typer.Context` if not passed.
    """

    def decorator(func: GenericFunction) -> GenericFunction:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            # Make a console copy since it cannot be re-assigned inside wrapper
            _console = console
            if _console is None:
                ctx = kwargs.get("ctx")
                _console = ctx.obj.console_stderr  # type: ignore

            try:
                func(*args, **kwargs)

            except HandledException as e:
                print_error(_console, e.msg)
                e.exit()

            except KeyboardInterrupt:
                print_error(_console, "Operation cancelled by user.")
                raise typer.Exit(ERR_KEYBOARD_INTERRUPT)

            except typer.Exit:
                raise

            except Exception as e:
                print_error(_console, f"Unexpected error: {e}")
                raise typer.Exit(ERR_UNEXPECTED)

        return wrapper  # type: ignore

    return decorator
