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
CERT = _ROOT / "server-cert.crt"
PRIV_KEY = _ROOT / "server-key.key"


# ----------------------
# Values
# ----------------------

ACCESS_TOKEN = "dummy-access-token"
CLIENT_TOKEN = "dummy-client-token"
INVALID_ACCESS_TOKEN = "invalid-access-token"
INVALID_CLIENT_TOKEN = "invalid-client-token"
