Troubleshooting
===============

This page covers the most common errors you may encounter while using ``akcli``, what they
mean, and how to resolve them.

All errors include an exit code that can be useful for scripting or debugging.

Authentication errors
---------------------

**Invalid credentials** (exit code 12)
   The API returned a ``401`` or ``403`` response. This usually means your EdgeGrid credentials
   are incorrect or expired.

   - Check that your ``.edgerc`` file exists and is correctly formatted.
   - Verify that the section you are using (``--edgerc-section``) has the right permissions for
   the endpoint you are trying to reach.
   - Make sure your credentials have not expired in the Akamai Control Center.

**Invalid .edgerc section** (exit code 70)
   The section specified via ``--edgerc-section`` or ``edgerc_section`` in the config file was
   not found in your ``.edgerc`` file.

   - Run ``cat ~/.edgerc`` and verify that the section name exists.
   - Section names are case-sensitive.

Network errors
--------------

**Request timeout** (exit code 14)
   The request to the Akamai API did not complete within the configured timeout.

   - Increase ``request_timeout`` in your config file or pass ``--request-timeout`` with a
   higher value.
   - Check your network connectivity.

**Proxy error** (exit code 18)
   ``akcli`` could not connect to the configured proxy.

   - Verify that the proxy URL set in ``proxy`` is correct and reachable.
   - To disable the proxy, remove the ``proxy`` option from your config file.

**SSL error** (exit code 21)
   An SSL error occurred while connecting to the API. This can happen in environments with
   custom certificate authorities or SSL inspection.

   - If you are in a controlled environment, you can disable SSL validation with
   ``--no-validate-certs`` or by setting ``validate_certs = false`` in your config file.

   .. warning::
      Disabling SSL certificate validation exposes your connection to potential security risks.
      Only do this in trusted environments.

**Too many requests** (exit code 17)
   The Akamai API has rate limited your client.

   - Wait a few seconds before retrying.
   - If this happens frequently, consider enabling caching (``use_cache = true``) to reduce the
   number of requests made to the API.

**Max polling attempts exceeded** (exit code 20)
   Some Akamai API operations are asynchronous and require polling until completion. This error
   means the operation did not complete within the maximum number of polling attempts.

   - This is usually a transient issue on the API side. Retry the command after a few seconds.

API errors
----------

**Resource not found** (exit code 11)
   The requested resource does not exist on the API.

   - Double-check the arguments passed to the command (hostname, error ID, etc.).

**Bad request** (exit code 19)
   The API rejected the request as malformed or invalid.

   - Review the arguments passed to the command.
   - Run the command with ``--json`` to inspect the full API error response.

**Method not allowed** (exit code 16)
   The HTTP method used is not allowed for the endpoint. This is likely an internal ``akcli``
   issue.

   - Please open an issue on `GitHub <https://github.com/jvicg/akcli/issues>`_.

**Invalid response** (exit code 13)
   The API returned a response that ``akcli`` could not parse.

  - This may be a temporary issue on the API side. Retry the command.
  - Run the command with ``--json`` to inspect the raw response.

**Unexpected request error** (exit code 15)
   An unhandled error occurred during the request.

   - Check your network connectivity and retry.
   - If the issue persists, open an issue on `GitHub <https://github.com/jvicg/akcli/issues>`_.

Configuration errors
--------------------

**The** ``--help`` **shows a path that does not exist**
   If you have set a custom ``cache_dir`` in your config file that no longer exists, ``akcli``
   will display it as the default value in ``--help``. The error will only appear when running
   an actual command.

   - Update ``cache_dir`` in your config file to a valid path, or remove it to fall back to
   the system default.

Caching issues
--------------

**Receiving the same response repeatedly**
   ``akcli`` caches API responses by default to avoid unnecessary requests. If you are expecting
   updated results — for example, after a configuration change or a DNS propagation — but keep
   getting the same response, the cache may be serving a stale result.

   - Disable caching temporarily with ``--no-use-cache``.
   - Alternatively, lower the cache TTL by setting a smaller value for ``cache_ttl`` in your
   config file or passing ``--cache-ttl`` with a shorter value in seconds.
   - If you need every request to reach the API without exception, set ``use_cache = false``
   in your config file for the duration of your testing.
