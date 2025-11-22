#!/usr/bin/env python3

"""
Module that exposes the model `TranslateReponse` which defines the API response to the endpoint: /edge-diagnostics/v1/error-translator
Some of the response objects are not defined in this module so will be ignored, since they're not considered useful.
Reference: https://techdocs.akamai.com/edge-diagnostics/reference/post-error-translator

Generated with `datamodel-code-generator` (https://github.com/koxudaxi/datamodel-code-generator)
and refined with manual adjustments.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .base_response import BaseResponse, CamelCaseModel, IpType


class Request(CamelCaseModel):
    error_code: Optional[str] = None
    trace_forward_logs: Optional[bool] = None


class Log(CamelCaseModel):
    arl: Optional[str] = None
    bytes_received: Optional[str] = None
    bytes_served: Optional[str] = None
    client_ip: Optional[str] = None
    content_bytes_served: Optional[str] = None
    content_type: Optional[str] = None
    cookie: Optional[str] = None
    cp_code: Optional[str] = None
    date_time: Optional[str] = None
    edge_ip: Optional[str] = None
    error: Optional[str] = None
    forward_ip: Optional[str] = None
    host_header: Optional[str] = None
    http_method: Optional[str] = None
    http_status: Optional[str] = None
    log_type: Optional[str] = None
    object_size: Optional[str] = None
    object_status: Optional[str] = None
    object_status2: Optional[str] = None
    object_status3: Optional[str] = None
    referer: Optional[str] = None
    ssl_version: Optional[str] = None
    time_taken: Optional[str] = None
    turnaround_time: Optional[str] = None
    user_agent: Optional[str] = None


class LogLines(CamelCaseModel):
    logs: List[Log] = Field(default_factory=list)


class Result(CamelCaseModel):
    cache_key_hostname: Optional[str] = None
    client_ip: IpType = Field(default_factory=IpType)
    client_request_method: Optional[str] = None
    connecting_ip: IpType = Field(default_factory=IpType, title="Connecting IP.")
    cp_code: Optional[int] = None
    date: Optional[str] = None
    edge_server_ip: IpType = Field(default_factory=IpType)
    epoch_time: Optional[int] = None
    grep_url: Optional[str] = None
    http_response_code: Optional[int] = None
    log_lines: LogLines = Field(default_factory=LogLines)
    origin_ip: Optional[str] = None
    property_name: Optional[str] = None
    property_url: Optional[str] = None
    reason_for_failure: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    waf_details: Optional[str] = None
    waf_details_url: Optional[str] = None
    wsa_url: Optional[str] = None
    no_logs: Optional[str] = Field(alias="noLogsErrorTitle", default=None)


class TranslateResponse(BaseResponse):
    request: Optional[Request] = None
    request_id: Optional[int] = None
    result: Result = Field(default_factory=Result)
    sugested_actions: List[str] = Field(default_factory=list)
