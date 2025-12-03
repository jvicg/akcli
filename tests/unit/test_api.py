#!/usr/bin/env python3

"""
Suite of tests for `AkamaiAPI` class.
"""

from configparser import NoSectionError
from itertools import product
from unittest.mock import MagicMock, patch

import pytest
from akamai.edgegrid import EdgeRc
from requests import Session
from requests.exceptions import HTTPError, ProxyError, Timeout

from akcli.api import AkamaiAPI, _poll_if_needed
from akcli.cache import Cache
from akcli.exceptions import (
    BadRequest,
    InvalidCredentials,
    InvalidEdgeRcSection,
    MaxAttempsExceeded,
    MethodNotAllowed,
    RequestError,
    RequestProxyError,
    RequestTimeout,
    ResourceNotFound,
    TooManyRequests,
)

# ----------------------
# Fixtures
# ----------------------


@pytest.fixture
def method():
    return "GET"


@pytest.fixture
def method_post():
    return "POST"


@pytest.fixture
def payload():
    return {"key": "value"}


@pytest.fixture
def endpoint():
    return "/test/endpoint"


@pytest.fixture
def base_url():
    return "dummy.com"


@pytest.fixture
def timeout():
    return 5


@pytest.fixture
def edgerc_path(tmp_path):
    return tmp_path / ".edgerc"


@pytest.fixture
def section():
    return "default"


@pytest.fixture
def mock_edgerc_obj():
    return MagicMock(spec=EdgeRc)


@pytest.fixture
def mock_cache():
    return MagicMock(spec=Cache)


@pytest.fixture
def mock_api(base_url, timeout, edgerc_path, section, mock_cache, mock_edgerc_obj):
    """
    Fixture that provides a mocked AkamaiAPI instance.
    """
    api = AkamaiAPI.__new__(AkamaiAPI)
    api._edgerc_path = edgerc_path
    api._edgerc_obj = mock_edgerc_obj
    api._section = section
    api._base_url = base_url
    api._timeout = timeout
    api._session = MagicMock(spec=Session)
    api._session.proxies = {
        "http": "http://proxyserver:8080",
        "https": "https://proxyserver:8080",
    }
    api._session.verify = False
    api._session.headers = {"Some": "Header"}
    api._cache = mock_cache
    return api


# ----------------------
# Tests
# ----------------------


def test_repr(mock_api):
    """
    Test the string representation of AkamaiAPI object.
    """
    r = repr(mock_api)
    assert "AkamaiAPI" in r
    assert mock_api._section in r
    assert str(mock_api._edgerc_path) in r


def test_edgerc_methods_are_called(edgerc_path, section, mock_edgerc_obj, mock_cache):
    """
    Test that all the methods related to edgerc are called with the expected params.
    """
    with (
        patch("akcli.api.EdgeRc", return_value=mock_edgerc_obj) as mock_edgerc,
        patch("akcli.api.EdgeGridAuth.from_edgerc") as mock_from_edgerc,
    ):
        AkamaiAPI(
            edgerc=edgerc_path,
            section=section,
            timeout=5,
            cache=mock_cache,
        )

    mock_edgerc.assert_called_once_with(edgerc_path.resolve())
    mock_from_edgerc.assert_called_once_with(mock_edgerc_obj, section)


def test_build_base_url(section, mock_edgerc_obj):
    """
    Test that `_build_base_url` method works as expected.
    """
    api = AkamaiAPI.__new__(AkamaiAPI)
    api._section = section
    api._edgerc_obj = mock_edgerc_obj
    api._edgerc_obj.get.return_value = "dummy.com"

    build_url = api._build_base_url()

    assert build_url == "https://dummy.com"


def test_build_base_url_raises_exception_on_invalid_section(mock_api):
    """
    Test that `_build_base_url` raises `InvalidEdgeRcSection` when section is invalid.
    """
    mock_api._edgerc_obj.get.side_effect = NoSectionError("error")

    with pytest.raises(InvalidEdgeRcSection):
        mock_api._build_base_url()


def test_build_base_headers(mock_api):
    """
    Test that `_build_base_headers` works as expected.
    """
    headers = mock_api._build_base_headers()

    assert isinstance(headers, dict) or hasattr(headers, "get")
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"

    # Ensure user agent includes project name and version dynamically
    from akcli.__version__ import __title__, __version__

    assert f"{__title__}/{__version__}" in headers["User-Agent"]


@pytest.mark.parametrize(
    "proxy, verify, cert",
    list(
        product(
            [None, "http://proxyserver:8080"],
            [True, False],
            [None, ("/path/to/cert.pem", "/path/to/key.pem")],
        )
    ),
)
def test_session_configuration(edgerc_path, section, mock_cache, proxy, verify, cert):
    """
    Test that `Session` is configured as expected.
    """
    with (
        patch("akcli.api.requests.Session") as mock_session,
        patch("akcli.api.EdgeRc"),
        patch("akcli.api.EdgeGridAuth.from_edgerc"),
        patch("akcli.api.AkamaiAPI._build_base_url"),
    ):
        AkamaiAPI(
            edgerc=edgerc_path,
            section=section,
            timeout=5,
            cache=mock_cache,
            verify=verify,
            proxy=proxy,
            cert=cert,
        )

    mock_session.assert_called_once()

    assert mock_session.return_value.cert == cert
    assert mock_session.return_value.verify == verify

    assert (
        mock_session.return_value.proxies == {"http": "", "https": ""}
        if proxy is None
        else {"http": proxy, "https": proxy}
    )


@pytest.mark.parametrize(
    "method, endpoint, json, headers",
    list(
        product(
            ["GET", "POST", "PUT", "DELETE"],
            ["/test/endpoint", "/another/endpoint/"],
            [None, {"a": 1, "b": 2}],
            [None, {"Custom-Header": "Value"}],
        )
    ),
)
def test_request_call_with_expected_params(
    base_url, timeout, mock_api, method, endpoint, json, headers
):
    """
    Test that `_request_build_url` method constructs URLs correctly.
    """
    url = base_url + endpoint

    # Call the method avoiding decorators
    mock_api._request.__wrapped__(
        mock_api, method, endpoint, json=json, headers=headers
    )

    mock_api._session.request.assert_called_once_with(
        method, url, timeout=timeout, json=json, headers=headers
    )


def test_request_returns_json_on_200(mock_api):
    """
    Test that `_request` method returns JSON response on 200 status code.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True}

    mock_api._session.request.return_value = mock_resp

    result = mock_api._request.__wrapped__(mock_api, "GET", "/some/endpoint/")

    assert result == {"ok": True}


def _call_request(mock_api, method, endpoint, status_code):
    """
    Helper function to simulate a request returning a specific status code and raising HTTPError.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {"error": "Some error occurred"}
    mock_resp.raise_for_status.side_effect = HTTPError()

    mock_api._session.request.return_value = mock_resp

    return mock_api._request.__wrapped__(mock_api, method, endpoint)


@pytest.mark.parametrize(
    "status_code, raised_exception",
    [
        (400, BadRequest),
        (401, InvalidCredentials),
        (403, InvalidCredentials),
        (404, ResourceNotFound),
        (405, MethodNotAllowed),
        (429, TooManyRequests),
    ],
)
def test_request_raises_exception_on_non_200(
    mock_api, method, endpoint, status_code, raised_exception
):
    """
    Test that `_request` method raises an exception on non-200 status codes.
    """
    with pytest.raises(raised_exception):
        _call_request(mock_api, method, endpoint, status_code)


@pytest.mark.parametrize(
    "request_exception, raised_exception",
    [
        (Timeout, RequestTimeout),
        (ProxyError, RequestProxyError),
        (Exception, RequestError),
    ],
)
def test_request_raises_exception_on_timeout_proxy_or_unhandled_error(
    mock_api, method, endpoint, request_exception, raised_exception
):
    """
    Test that `_request` method raises `RequestTimeout`, `ProxyError`, or `RequestError` on unhandled exceptions.
    """
    mock_api._session.request.side_effect = request_exception()

    with pytest.raises(raised_exception):
        mock_api._request.__wrapped__(mock_api, method, endpoint)


@pytest.mark.parametrize("status_code", [499, 502, 503, 504])
def test_request_raises_exception_on_unhandled_status_code(
    mock_api, method, endpoint, status_code
):
    """
    Test that `_request` method raises `RequestError` on unhandled status codes.
    """
    with pytest.raises(RequestError):
        _call_request(mock_api, method, endpoint, status_code)


@pytest.mark.parametrize(
    "func_name, method, json, headers",
    [
        ("_get", "GET", None, None),
        ("_delete", "DELETE", None, None),
        ("_post", "POST", {"key": "value"}, {"some": "header"}),
        ("_patch", "PATCH", {"key": "value"}, {"other": "header"}),
    ],
)
def test_request_wrappers_call_request_with_expected_params(
    mock_api, func_name, method, json, headers, endpoint
):
    """
    Test that _get/_post/_patch/_delete methods call `_request` with correct params.
    """
    kwargs = {"json": json} if json is not None else {}
    kwargs["headers"] = headers

    with patch.object(mock_api, "_request", return_value={"ok": True}) as mock_request:
        func = getattr(mock_api, func_name)
        result = func(endpoint=endpoint, **kwargs)

    mock_request.assert_called_once_with(method=method, endpoint=endpoint, **kwargs)

    assert result == {"ok": True}


def test_poll_if_needed_raises_exception_when_exceed_maximum_retries(method, endpoint):
    """
    Test that `_poll_if_needed` raises an exception when maximum retries are exceeded.
    """
    pending_response = {"executionStatus": "IN_PROGRESS"}

    mock_request = MagicMock(
        return_value=pending_response
    )  # Always return pending response
    decorated_func = _poll_if_needed(mock_request)

    with (
        patch("akcli.api.sleep"),
        pytest.raises(MaxAttempsExceeded),
    ):
        decorated_func(method, endpoint)


def test_poll_changes_method_to_get_in_subsequent_cycles(
    endpoint, method_post, payload
):
    """
    Test that `_poll_if_needed` changes method to GET in subsequent polling cycles.
    """
    pending_response = {
        "executionStatus": "IN_PROGRESS",
        "link": "/dummy/polling/endpoint",
        "retryAfter": 0,
    }
    completed_response = {"executionStatus": "COMPLETED", "data": {"result": "ok"}}

    mock_request = MagicMock(
        side_effect=[pending_response, pending_response, completed_response]
    )
    decorated_func = _poll_if_needed(mock_request)

    with patch("akcli.api.sleep"):
        result = decorated_func(method=method_post, endpoint=endpoint, json=payload)

    assert result == completed_response
    assert mock_request.call_count == 3

    assert mock_request.call_args_list[0].kwargs == {
        "method": method_post,
        "endpoint": endpoint,
        "json": payload,
    }

    assert mock_request.call_args_list[1].kwargs == {
        "method": "GET",
        "endpoint": "/dummy/polling/endpoint",
    }

    assert mock_request.call_args_list[2].kwargs == {
        "method": "GET",
        "endpoint": "/dummy/polling/endpoint",
    }
