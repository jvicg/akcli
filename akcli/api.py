#!/usr/bin/env python

"""
HTTP session management, authentication, and request handling for Akamai's API.
"""

from configparser import NoSectionError
from functools import wraps
from json import dumps
from pathlib import Path
from time import sleep
from typing import Any, Optional

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from pydantic_core import ValidationError

from . import __title__, __version__
from .cache import Cache, cached
from .exceptions import (
    BadRequest,
    InvalidCredentials,
    InvalidEdgeRcSection,
    InvalidResponse,
    MaxAttempsExceeded,
    MethodNotAllowed,
    ProxyError,
    RequestError,
    RequestTimeout,
    ResourceNotFound,
    TooManyRequests,
)
from .models import DigResponse, TranslateResponse
from .typing import Certificate, GenericFunction, Headers, JSONResponse
from .utils import highlight

_MAX_POLLING_ATTEMPTS = 15


def _poll_if_needed(func: GenericFunction) -> GenericFunction:
    """
    Helper decorator to poll the API if the operation is still in progress.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
        attempt = kwargs.pop("_poll_attempt", 0)
        data = func(*args, **kwargs)
        exec_status = data.get("executionStatus", "")

        if exec_status != "IN_PROGRESS":
            return data

        # Prevent infinite recursion in case the API never completes
        if attempt > _MAX_POLLING_ATTEMPTS:
            raise MaxAttempsExceeded("Polling exceeded maximum number of attempts.")

        wait = data.get("retryAfter", 0)
        sleep(wait)

        # Prepare next polling request
        kwargs["method"] = "GET"
        kwargs["endpoint"] = data.get("link")
        kwargs["_poll_attempt"] = attempt + 1

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
        validate_certs: bool = True,
        proxy: Optional[str] = None,
        cert: Optional[Certificate] = None,
    ) -> None:
        self._edgerc_path = edgerc.resolve()
        self._edgerc_obj = EdgeRc(self._edgerc_path)
        self._section = section
        self._cache = cache
        self._base_url = self._build_base_url()
        self._validate_certs = validate_certs
        self._timeout = timeout

        # Disable warnings for insecure certificate
        if not self._validate_certs:
            from urllib3 import disable_warnings
            from urllib3.exceptions import InsecureRequestWarning

            disable_warnings(category=InsecureRequestWarning)

        # Session configuration
        self._session = requests.Session()
        self._session.cert = cert
        self._session.auth = EdgeGridAuth.from_edgerc(self._edgerc_obj, self._section)
        self._session.proxies = (
            {"http": "", "https": ""}
            if proxy is None
            else {"http": proxy, "https": proxy}
        )
        self._session.headers = self._build_base_headers()

    def __repr__(self) -> str:
        """
        String representation of the AkamaiAPI object for debugging purposes.
        """
        return (
            f"<AkamaiAPI "
            f"section='{self._section}', "
            f"base_url='{self._base_url}', "
            f"edgerc='{self._edgerc_path}'>"
        )

    def _build_base_url(self) -> str:
        """
        Build API's base url.
        """
        try:
            return "https://" + self._edgerc_obj.get(self._section, "host")

        except NoSectionError:
            raise InvalidEdgeRcSection(
                f"The section '{highlight(self._section)}' was not found in the file: {highlight(str(self._edgerc_path))}."
            )

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

    @cached
    @_poll_if_needed
    def _request(
        self, method: str, endpoint: str, *args: Any, **kwargs: Any
    ) -> JSONResponse:
        """
        Generic function to make a request.
        """
        url = self._base_url + endpoint

        kwargs["timeout"] = self._timeout
        kwargs["verify"] = self._validate_certs

        # Initialize `res` to None for preventing `UnboundLocalError` in some hypothetical scenarios
        res = None

        try:
            res = self._session.request(method, url, **kwargs)
            res.raise_for_status()
            return res.json()

        except requests.exceptions.HTTPError:
            if res is not None:
                if res.status_code == 400:
                    error_body = dumps(res.json(), indent=2)
                    raise BadRequest(
                        f"API returned BadRequest response: \n\n{error_body}"
                    )
                elif res.status_code in (401, 403):
                    raise InvalidCredentials(
                        f"Unable to authenticate with the Akamai API. Check EdgeGrid file: {highlight(str(self._edgerc_path))}."
                    )
                elif res.status_code == 404:
                    raise ResourceNotFound(
                        f"The endpoint '{highlight(endpoint)}' was not found on the server."
                    )
                elif res.status_code == 405:
                    raise MethodNotAllowed(
                        f"The method '{highlight(method)}' is not allowed for the endpoint '{highlight(endpoint)}'."
                    )
                elif res.status_code == 429:
                    raise TooManyRequests(
                        "Too many requests. You have been rate limited by the API."
                    )
                else:
                    raise

            # In case `res` is None, re-raise the exception
            raise

        except requests.exceptions.Timeout:
            raise RequestTimeout(
                f"The request timed after {highlight(str(self._timeout))} seconds."
            )

        except requests.exceptions.ProxyError:
            raise ProxyError(
                f"Unable to connect to proxy {highlight(self._session.proxies['http'])}"
            )

        except ValidationError as e:
            raise InvalidResponse(f"Response validation error: {e}")

        except Exception as e:
            raise RequestError(f"An error occurred while making the request: {e}")

    def _get(self, endpoint: str, headers: Optional[Headers] = None) -> JSONResponse:
        """
        Make a GET request.
        """
        return self._request(method="GET", endpoint=endpoint, headers=headers)

    def _post(
        self, endpoint: str, payload: dict, headers: Optional[Headers] = None
    ) -> JSONResponse:
        """
        Make a POST request.
        """
        return self._request(
            method="POST", endpoint=endpoint, json=payload, headers=headers
        )

    def _patch(
        self, endpoint: str, payload: dict, headers: Optional[Headers] = None
    ) -> JSONResponse:
        """
        Make a PATCH request.
        """
        return self._request(
            method="PATCH", endpoint=endpoint, json=payload, headers=headers
        )

    def _delete(self, endpoint: str, headers: Optional[Headers] = None) -> JSONResponse:
        """
        Make a DELETE request.
        """
        return self._request(method="DELETE", endpoint=endpoint, headers=headers)

    def dig(self, hostname: str, query_type: str) -> DigResponse:
        """
        Uses `dig` command using an Akamai Edge server.
        Reference: https://techdocs.akamai.com/edge-diagnostics/reference/post-dig
        """
        endpoint = "/edge-diagnostics/v1/dig"
        payload = {
            "isGtmHostname": False,
            "queryType": query_type,
            "hostname": hostname,
        }

        data = self._post(endpoint=endpoint, payload=payload)

        return DigResponse.model_validate(data)

    def translate(self, id: str, trace: bool) -> TranslateResponse:
        """
        Translate an Akamai Error String.
        Reference: https://techdocs.akamai.com/edge-diagnostics/reference/post-error-translator
        """
        endpoint = "/edge-diagnostics/v1/error-translator"
        payload = {"errorCode": id, "traceForwardLogs": trace}

        data = self._post(endpoint=endpoint, payload=payload)

        return TranslateResponse.model_validate(data)
