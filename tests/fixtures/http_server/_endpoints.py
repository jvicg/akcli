#!/usr/bin/env python3

"""
Definition of the endpoints of the server.

Some of the code here is inspired by https://github.com/httpie/cli/blob/master/tests/utils/http_server.py
"""

import json
from http import HTTPStatus
from pathlib import Path
from time import sleep

from tests.fixtures.constants import (
    DIG_NO_RECORDS_RESPONSE,
    DIG_SUCCESS_RESPONSE,
    DIG_TIMEOUT_HOSTNAME,
    DIG_VALID_HOSTNAME,
    PURGE_BAD_REQUEST_TRIGGER,
    PURGE_SUCCESS_RESPONSE,
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

from ._http_server import HTTPRequestHandler


def _parse_file_into_bytes(path: Path) -> bytes:
    """
    Helper function to read a JSON file and return its content as bytes.
    """
    with path.open("r") as f:
        return json.dumps(json.load(f)).encode("utf-8")


# -----------------------
# General endpoints
# -----------------------


@HTTPRequestHandler.endpoint("GET", "/headers")
def get_headers(handler: HTTPRequestHandler) -> None:
    """
    A simple endpoint that returns the request headers.
    """
    handler.send_response(HTTPStatus.OK)

    for k, v in handler.headers.items():
        handler.send_header(k, v)

    handler.send_header("Content-Length", "0")
    handler.end_headers()


# -----------------------
# Dig endpoints
# -----------------------


@HTTPRequestHandler.endpoint("POST", "/edge-diagnostics/v1/dig")
def dig_response(handler: HTTPRequestHandler) -> None:
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


# -----------------------
# Translate endpoints
# -----------------------


@HTTPRequestHandler.endpoint("POST", "/edge-diagnostics/v1/error-translator")
def post_translate_response(handler: HTTPRequestHandler) -> None:
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


@HTTPRequestHandler.endpoint("GET", "/edge-diagnostics/v1/error-translator/requests/30x-response-id")
def get_translate_response_30x(handler: HTTPRequestHandler) -> None:
    """
    Endpoint that simulates fetching the translated 30x codes.
    """
    sent_data = _parse_file_into_bytes(TRANSLATE_30X_CODES_RESPONSE)
    return handler.send_ok(sent_data)


@HTTPRequestHandler.endpoint("GET", "/edge-diagnostics/v1/error-translator/requests/non-30x-response-id")
def get_translate_response_non_30x(handler: HTTPRequestHandler) -> None:
    """
    Endpoint that simulates fetching the translated non-30x codes.
    """
    sent_data = _parse_file_into_bytes(TRANSLATE_NON_30X_CODES_RESPONSE)
    return handler.send_ok(sent_data)


@HTTPRequestHandler.endpoint("GET", "/edge-diagnostics/v1/error-translator/requests/no-logs-response-id")
def get_translate_response_no_logs(handler: HTTPRequestHandler) -> None:
    """
    Endpoint that simulates fetching when there are no logs available.
    """
    sent_data = _parse_file_into_bytes(TRANSLATE_NO_LOGS_RESPONSE)
    return handler.send_ok(sent_data)


# -----------------------
# Purge endpoints
# -----------------------


@HTTPRequestHandler.endpoint("POST", "/ccu/v3")
def post_purge_invalidate_url(handler: HTTPRequestHandler) -> None:
    """
    Generic endpoint for all the purge calls. This endpoint covers the endpoints:
        - /ccu/v3/invalidate/url/staging
        - /ccu/v3/invalidate/url/production
    and so on.
    """
    data = handler.get_post_data()

    if PURGE_BAD_REQUEST_TRIGGER in data.get("objects", []):
        return handler.send_bad_request()

    sent_data = _parse_file_into_bytes(PURGE_SUCCESS_RESPONSE)
    return handler.send_ok(sent_data)
