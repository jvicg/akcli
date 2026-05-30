#!/usr/bin/env python

"""
HTTP session management, authentication, and request handling for Akamai's API.
"""

import json
from configparser import NoSectionError
from functools import wraps
from pathlib import Path
from time import sleep
from typing import Any, List, Optional

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc

from akcli.models.nl_response import NLResponse

from .__version__ import __title__, __version__
from .cache import Cache, cached
from .exceptions import (
    BadRequest,
    InvalidCredentials,
    InvalidEdgeRcSection,
    MaxAttempsExceeded,
    MethodNotAllowed,
    RequestError,
    RequestProxyError,
    RequestSSLError,
    RequestTimeout,
    ResourceNotFound,
    TooManyRequests,
)
from .models import DigResponse, PurgeResponse, TranslateResponse
from .typing import Certificate, GenericFunction, Headers, JSONResponse
from .utils import highlight

_MAX_POLLING_ATTEMPTS = 15


def _poll_if_needed(func: GenericFunction) -> GenericFunction:
    """
    Helper decorator to poll the API if the operation is still in progress.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
        attempt = kwargs.pop("_poll_attempt", 1)
        data = func(*args, **kwargs)
        exec_status = data.get("executionStatus", "")

        if exec_status != "IN_PROGRESS":
            return data

        # Prevent infinite recursion in case the API never completes
        if attempt >= _MAX_POLLING_ATTEMPTS:
            raise MaxAttempsExceeded("Polling exceeded maximum number of attempts.")

        wait = data.get("retryAfter", 0)
        sleep(wait)

        # Prepare next polling request
        kwargs["method"] = "GET"
        kwargs["endpoint"] = data.get("link")
        kwargs["_poll_attempt"] = attempt + 1
        kwargs.pop("json", None)  # Remove payload if present

        # Recursively continue polling until the operation is done
        return wrapper(*args, **kwargs)

    return wrapper  # type: ignore


class AkamaiAPI:
    """
    Handles authentication, session management, and HTTP operations (GET, POST, PATCH, DELETE)
    and exposes methods for interacting with Akamai's API endpoints.
    """

    def __init__(
        self,
        edgerc: Path,
        section: str,
        timeout: int,
        cache: Cache,
        verify: bool = True,
        proxy: Optional[str] = None,
        cert: Optional[Certificate] = None,
    ) -> None:
        self._edgerc_path = edgerc.expanduser().resolve()
        self._edgerc_obj = EdgeRc(self._edgerc_path)
        self._section = section
        self._cache = cache
        self._base_url = self._build_base_url()
        self._timeout = timeout

        # Disable warnings for insecure certificate
        if not verify:
            from urllib3 import disable_warnings
            from urllib3.exceptions import InsecureRequestWarning

            disable_warnings(category=InsecureRequestWarning)

        # Session configuration
        self._session = requests.Session()
        self._session.cert = cert
        self._session.verify = verify
        self._session.auth = EdgeGridAuth.from_edgerc(self._edgerc_obj, self._section)
        self._session.proxies = {"http": "", "https": ""} if proxy is None else {"http": proxy, "https": proxy}
        self._session.headers = self._build_base_headers()

    def __repr__(self) -> str:
        """
        String representation of the AkamaiAPI object for debugging purposes.
        """
        return f"<AkamaiAPI section='{self._section}', base_url='{self._base_url}', edgerc='{self._edgerc_path}'>"

    def _build_base_url(self) -> str:
        """
        Build API's base url.
        """
        try:
            return "https://" + self._edgerc_obj.get(self._section, "host")

        except NoSectionError as e:
            raise InvalidEdgeRcSection(
                f"The section '{highlight(self._section)}' was not found in EdgeGrid file: {self._edgerc_path!s}."
            ) from e

    def _build_base_headers(self) -> Headers:
        """
        Build base headers for requests.
        """
        return Headers(
            {
                "User-Agent": f"{__title__}/{__version__}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    # NOTE: cached wraps poll_if_needed because we only want to cache the final response
    @cached
    @_poll_if_needed
    def _request(self, method: str, endpoint: str, *args: Any, **kwargs: Any) -> JSONResponse:
        """
        Generic function to make a request.
        """
        url = self._base_url + endpoint

        kwargs["timeout"] = self._timeout

        # Initialize `res` to None for preventing `UnboundLocalError` in some hypothetical scenarios
        res = None

        try:
            res = self._session.request(method, url, **kwargs)
            res.raise_for_status()
            return res.json()

        except requests.exceptions.HTTPError as e:
            if res is not None:
                if res.status_code == 400:
                    error_body = json.dumps(res.json(), indent=2)
                    raise BadRequest(f"API returned BadRequest response: \n\n{error_body}") from e
                elif res.status_code in (401, 403):
                    raise InvalidCredentials(
                        "Unable to authenticate with the Akamai API. "
                        f"Check EdgeGrid file: {highlight(str(self._edgerc_path))}."
                    ) from e
                elif res.status_code == 404:
                    raise ResourceNotFound(f"The endpoint '{highlight(endpoint)}' was not found on the server.") from e
                elif res.status_code == 405:
                    raise MethodNotAllowed(
                        f"The method '{highlight(method)}' is not allowed for the endpoint '{highlight(endpoint)}'."
                    ) from e
                elif res.status_code == 429:
                    raise TooManyRequests("Too many requests. You have been rate limited by the API.") from e
                else:
                    error_body = json.dumps(res.json(), indent=2)
                    raise RequestError(f"Unhandled HTTP {res.status_code} error: \n\n{error_body}") from e

            # In case `res` is None, re-raise the exception
            raise

        except requests.exceptions.Timeout as e:
            raise RequestTimeout(f"The request timed out after {highlight(str(self._timeout))} seconds.") from e

        except requests.exceptions.SSLError as e:
            raise RequestSSLError(f"An SSL error occurred while connecting to the API: {e}") from e

        except requests.exceptions.ProxyError as e:
            raise RequestProxyError(f"Unable to connect to proxy {highlight(self._session.proxies['http'])}") from e

        except Exception as e:
            raise RequestError(f"An error occurred while making the request: {e}") from e

    def _get(self, endpoint: str, use_cache: bool = True, **kwargs) -> JSONResponse:
        """
        Make a GET request.
        """
        return self._request(method="GET", endpoint=endpoint, use_cache=use_cache, **kwargs)

    def _post(self, endpoint: str, use_cache: bool = True, **kwargs) -> JSONResponse:
        """
        Make a POST request.
        """
        return self._request(method="POST", endpoint=endpoint, use_cache=use_cache, **kwargs)

    def _patch(self, endpoint: str, use_cache: bool = True, **kwargs) -> JSONResponse:
        """
        Make a PATCH request.
        """
        return self._request(method="PATCH", endpoint=endpoint, use_cache=use_cache, **kwargs)

    def _delete(self, endpoint: str, use_cache: bool = True, **kwargs) -> JSONResponse:
        """
        Make a DELETE request.
        """
        return self._request(method="DELETE", endpoint=endpoint, use_cache=use_cache, **kwargs)

    def dig(self, hostname: str, query_type: str) -> DigResponse:
        """
        Uses `dig` command using an Akamai Edge server.
        - Reference: https://techdocs.akamai.com/edge-diagnostics/reference/post-dig
        """
        endpoint = "/edge-diagnostics/v1/dig"
        payload = {
            "isGtmHostname": False,
            "queryType": query_type,
            "hostname": hostname,
        }

        data = self._post(endpoint=endpoint, json=payload)

        return DigResponse.parse_model(data)

    def translate(self, id: str, trace: bool) -> TranslateResponse:
        """
        Translate an Akamai Error String.
        - Reference: https://techdocs.akamai.com/edge-diagnostics/reference/post-error-translator
        """
        endpoint = "/edge-diagnostics/v1/error-translator"
        payload = {"errorCode": id, "traceForwardLogs": trace}

        data = self._post(endpoint=endpoint, json=payload)

        return TranslateResponse.parse_model(data)

    def purge(self, method: str, network: str, purge_type: str, objects: List) -> PurgeResponse:
        """
        Purge content given CP code, tag or URL/ARL.
        - Reference: https://techdocs.akamai.com/purge-cache/reference/
        """
        endpoint = f"/ccu/v3/{method}/{purge_type}/{network}"
        payload = {"objects": objects}

        # Purge is a write operation — caching would silently skip the actual request
        data = self._post(endpoint=endpoint, json=payload, use_cache=False)

        return PurgeResponse.parse_model(data)

    def nl_list(self, list_type: str, search: str, include_elements: bool, extended: bool) -> NLResponse:
        """
        List all the Network Lists availables for authenticated user.
        - Reference: https://techdocs.akamai.com/network-lists/reference/get-network-lists
        """
        endpoint = "/network-list/v2/network-lists"
        params = {"listType": list_type, "search": search, "includeElements": include_elements, "extended": extended}

        data = self._get(endpoint=endpoint, params=params)

        return NLResponse.parse_model(data)
