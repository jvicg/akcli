#!/usr/bin/env python3

"""
Simple HTTPS server to simulate Akamai API and handle responses in the tests.

Some of the code here is inspired by https://github.com/httpie/cli/blob/master/tests/utils/http_server.py
"""

from __future__ import annotations

import json
import ssl
import threading
from collections import defaultdict
from contextlib import contextmanager
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from time import sleep
from typing import Any, Callable, Dict, Generator, Literal, Type
from urllib.parse import urlparse

from .constants import (
    ACCESS_TOKEN,
    CERT,
    CLIENT_TOKEN,
    DIG_NO_RECORDS_RESPONSE,
    DIG_SUCCESS_RESPONSE,
    DIG_TIMEOUT_HOSTNAME,
    DIG_VALID_HOSTNAME,
    PRIV_KEY,
    TRANSLATE_30X_CODES_RESPONSE,
    TRANSLATE_30X_ID,
    TRANSLATE_BAD_REQUEST_ID,
    TRANSLATE_NO_LOGS_RESPONSE,
    TRANSLATE_NON_30X_CODES_RESPONSE,
    TRANSLATE_NON_30X_ID,
    TRANSLATE_PENDING_30X_RESPONSE,
    TRANSLATE_PENDING_NO_LOGS_RESPONSE,
    TRANSLATE_PENDING_NON_30X_RESPONSE,
)

_StatusCode = Literal[HTTPStatus.OK, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]


def _parse_file_into_bytes(path: Path) -> bytes:
    """
    Helper function to read a JSON file and return its content as bytes.
    """
    with path.open("r") as f:
        return json.dumps(json.load(f)).encode("utf-8")


# -----------------------
# Requests Handler
# -----------------------


class _HTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP request handler.
    """

    handlers = defaultdict(dict)

    @classmethod
    def endpoint(
        cls: Type["_HTTPRequestHandler"], method: str, endpoint: str
    ) -> Callable[..., Any]:
        """
        Decorator to register a handler function for a specific HTTP method and endpoint.
        The function will be stored in the `handlers` dictionary with method and endpoint as keys.
        """

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            cls.handlers[method][endpoint] = func
            return func

        return wrapper

    def _resolve_handler(self) -> Callable[..., Any]:
        """
        Resolve the handler function based on the request method and path.
        """
        endpoint = urlparse(self.path).path
        method = self.command
        return self.handlers[method].get(endpoint)  # type: ignore

    def _do_generic(self) -> Any:
        """
        Generic handler for all HTTP methods.
        It will use the function stored in the `handlers` dictionary to process the request.
        """
        func = self._resolve_handler()

        if func is None:
            return self.send_error(HTTPStatus.NOT_FOUND)

        # Validate authentication for all endpoints
        status_code = self._validate_auth(ACCESS_TOKEN, CLIENT_TOKEN)

        if status_code != HTTPStatus.OK:
            return (
                self.send_unauthorized()
                if status_code == HTTPStatus.UNAUTHORIZED
                else self.send_forbidden()
            )

        return func(self)

    def _parse_auth_header(self, auth: str) -> Dict[str, str]:
        """
        Parse EdgeGrid Authorization header into a dictionary.
        Example return: {"access_token": "value", "client_token": "value"}
        """
        parts = auth.replace("EG1-HMAC-SHA256", "").strip().split(";")

        # Return only two first parts since we only need `access_token` and `client_token`
        return dict(p.split("=") for p in parts[:2])

    def _validate_auth(self, access_token: str, client_token: str) -> _StatusCode:
        """
        Validate EdgeGrid Authorization header. This function will simply check that `client_token`
        and `access_token` have the expected values. It won't validate the signature or timestamp.

        Returns `HTTPStatus.OK` if valid, `HTTPStatus.UNAUTHORIZED` if missing/invalid header,
        or `HTTPStatus.FORBIDDEN` if tokens do not match.
        """
        auth = self.headers.get("Authorization")

        if auth is None or not auth.startswith("EG1-HMAC-SHA256"):
            return HTTPStatus.UNAUTHORIZED

        token = self._parse_auth_header(auth)

        if (
            token.get("client_token") != client_token
            or token.get("access_token") != access_token
        ):
            return HTTPStatus.FORBIDDEN

        return HTTPStatus.OK

    def get_post_data(self) -> Dict[str, Any]:
        """
        Helper method to read and return the POST request body data.
        """
        content_length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(content_length)

        if not data:
            return {}

        return json.loads(data)

    def _send_generic(
        self,
        status_code: int,
        data: bytes = b"",
        content_type: str = "application/json",
    ) -> None:
        """
        Generic method to send a response with the given status code and data.
        """
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()

    def send_ok(self, data: bytes) -> None:
        """
        Return a 200 OK response.
        """
        self._send_generic(HTTPStatus.OK, data)

    def send_bad_request(self) -> None:
        """
        Return a 400 Bad Request response.
        """
        self._send_generic(HTTPStatus.BAD_REQUEST, b'{"error": "bad request"}')

    def send_forbidden(self) -> None:
        """
        Return a 403 Forbidden response.
        """
        self._send_generic(HTTPStatus.FORBIDDEN, b'{"error": "forbidden"}')

    def send_unauthorized(self) -> None:
        """
        Return a 401 Unauthorized response.
        """
        self._send_generic(HTTPStatus.UNAUTHORIZED, b'{"error": "unauthorized"}')

    def log_message(self, format, *args) -> None:
        return  # Suppress logging to keep test output clean

    do_GET = _do_generic
    do_POST = _do_generic


# -----------------------
# Endpoints
# -----------------------


@_HTTPRequestHandler.endpoint("GET", "/headers")
def get_headers(handler: _HTTPRequestHandler) -> None:
    """
    A simple endpoint that returns the request headers.
    """
    handler.send_response(HTTPStatus.OK)

    for k, v in handler.headers.items():
        handler.send_header(k, v)

    handler.send_header("Content-Length", "0")
    handler.end_headers()


@_HTTPRequestHandler.endpoint("POST", "/edge-diagnostics/v1/dig")
def dig_response(handler: _HTTPRequestHandler) -> None:
    """
    Endpoint that simulates the `dig` API.
    """
    data = handler.get_post_data()
    hostname = data.get("hostname", "")

    if hostname == DIG_VALID_HOSTNAME:
        response_file = DIG_SUCCESS_RESPONSE

    # Simulate a delay to trigger a timeout in the client
    elif hostname == DIG_TIMEOUT_HOSTNAME:
        sleep(1.5)
        return

    # Simulate no records found for other hostnames
    else:
        response_file = DIG_NO_RECORDS_RESPONSE

    sent_data = _parse_file_into_bytes(response_file)

    return handler.send_ok(sent_data)


@_HTTPRequestHandler.endpoint("POST", "/edge-diagnostics/v1/error-translator")
def post_translate_response(handler: _HTTPRequestHandler) -> None:
    """
    Endpoint that simulates the `translate` API.
    This endpoint will always return a pending response to simulate the real endpoint behavior.
    The response will indicate a link that has to be polled to get the actual translated logs.
    """
    data = handler.get_post_data()
    error_code = data.get("errorCode", "")

    if error_code == TRANSLATE_BAD_REQUEST_ID:
        return handler.send_bad_request()

    elif error_code == TRANSLATE_30X_ID:
        sent_data = _parse_file_into_bytes(TRANSLATE_PENDING_30X_RESPONSE)

    elif error_code == TRANSLATE_NON_30X_ID:
        sent_data = _parse_file_into_bytes(TRANSLATE_PENDING_NON_30X_RESPONSE)

    else:
        sent_data = _parse_file_into_bytes(TRANSLATE_PENDING_NO_LOGS_RESPONSE)

    return handler.send_ok(sent_data)


@_HTTPRequestHandler.endpoint(
    "GET", "/edge-diagnostics/v1/error-translator/requests/30x-response-id"
)
def get_translate_response_30x(handler: _HTTPRequestHandler) -> None:
    """
    Endpoint that simulates fetching the translated 30x codes.
    """
    sent_data = _parse_file_into_bytes(TRANSLATE_30X_CODES_RESPONSE)
    return handler.send_ok(sent_data)


@_HTTPRequestHandler.endpoint(
    "GET", "/edge-diagnostics/v1/error-translator/requests/non-30x-response-id"
)
def get_translate_response_non_30x(handler: _HTTPRequestHandler) -> None:
    """
    Endpoint that simulates fetching the translated non-30x codes.
    """
    sent_data = _parse_file_into_bytes(TRANSLATE_NON_30X_CODES_RESPONSE)
    return handler.send_ok(sent_data)


@_HTTPRequestHandler.endpoint(
    "GET", "/edge-diagnostics/v1/error-translator/requests/no-logs-response-id"
)
def get_translate_response_no_logs(handler: _HTTPRequestHandler) -> None:
    """
    Endpoint that simulates fetching when there are no logs available.
    """
    sent_data = _parse_file_into_bytes(TRANSLATE_NO_LOGS_RESPONSE)
    return handler.send_ok(sent_data)


# -----------------------
# Server context manager
# -----------------------


@contextmanager
def run_https_server() -> Generator[HTTPServer, None, None]:
    """
    Context manager that starts and stops a simple HTTPS server.
    Use threading to run the server in the background to avoid blocking the tests execution
    and dynamic port assignment to prevent address conflicts.
    """
    server = HTTPServer(
        ("localhost", 0), _HTTPRequestHandler
    )  # Set port to 0 for dynamic assignment

    # Wrap socket with SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT, keyfile=PRIV_KEY)
    server.socket = context.wrap_socket(server.socket, server_side=True)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    yield server

    server.shutdown()
    thread.join()
