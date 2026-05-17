#!/usr/bin/env python3

"""
Constants used in the tests.
"""

from pathlib import Path

# ----------------------
# Paths
# ----------------------

_ROOT = Path(__file__).parent.resolve() / "data"
EDGERC_TEMPLATE = _ROOT / "edgerc.template"
DIG_SUCCESS_RESPONSE = _ROOT / "dig_success_response.json"
DIG_NO_RECORDS_RESPONSE = _ROOT / "dig_no_records_response.json"
TRANSLATE_PENDING_RESPONSE = _ROOT / "translate_pending_response.json"
TRANSLATE_PENDING_30X_RESPONSE = _ROOT / "translate_pending_30.x_codes_response.json"
TRANSLATE_PENDING_NON_30X_RESPONSE = (
    _ROOT / "translate_pending_non_30.x_codes_response.json"
)
TRANSLATE_PENDING_NO_LOGS_RESPONSE = _ROOT / "translate_pending_no_logs_response.json"
TRANSLATE_30X_CODES_RESPONSE = _ROOT / "translate_30.x_codes_response.json"
TRANSLATE_NON_30X_CODES_RESPONSE = _ROOT / "translate_non_30.x_codes_response.json"
TRANSLATE_NO_LOGS_RESPONSE = _ROOT / "translate_no_logs_response.json"
CERT = _ROOT / "server-cert.crt"
PRIV_KEY = _ROOT / "server-key.key"


# ----------------------
# Values
# ----------------------

ACCESS_TOKEN = "dummy-access-token"
CLIENT_TOKEN = "dummy-client-token"
INVALID_ACCESS_TOKEN = "invalid-access-token"
INVALID_CLIENT_TOKEN = "invalid-client-token"

DIG_VALID_HOSTNAME = "www.example.com"
DIG_TIMEOUT_HOSTNAME = "force-timeout"
DIG_NO_RECORDS_HOSTNAME = "invalid-domain.notexists"

TRANSLATE_30X_ID = "successful-30x"
TRANSLATE_NON_30X_ID = "successful-non-30x"
TRANSLATE_NO_LOGS_ID = "successful-no-logs"
TRANSLATE_BAD_REQUEST_ID = "bad-request"
