Commands Usage
==============

``akcli`` is divided in different commands, each one oriented to a specific API endpoint
with its specific usage and configuration.

This section covers all available commands, their options, and how to configure them.
Each command has its own page with a full reference of flags and examples.

.. toctree::
   :caption: Reference
   :maxdepth: 1

   dig
   translate

Global configuration
~~~~~~~~~~~~~~~~~~~~

Before diving into each command, it is worth configuring the settings that apply across all of
them. These options control how ``akcli`` authenticates, caches responses, and connects to the
API — regardless of which command you run. They can be passed as flags before the command name
or persisted in the ``[main]`` section of the config file to avoid repeating them on every
invocation.

.. code-block:: bash

   akcli [OPTIONS] COMMAND [ARGS]...

Configuration file
------------------

``akcli`` supports a TOML config file to persist your preferred settings. To generate one with
all the default values run:

.. code-block:: bash

   akcli --init-config-file

When resolving the value of any option, ``akcli`` follows this order of priority:

1. **CLI flags** — always take precedence over everything else.
2. **Config file** — values set in the config file are used if no flag is provided.
3. **Defaults** — built-in default values are used if neither a flag nor a config file value is present.

Authentication
--------------

Before using ``akcli``, you need a valid EdgeGrid credentials file ``.edgerc`` to authenticate
with Akamai's API. Follow the official `EdgeGrid authentication guide
<https://techdocs.akamai.com/developer/docs/edgegrid>`_ to set it up.

- ``--edgerc PATH`` — Path to the EdgeGrid credentials file. Defaults to ``~/.edgerc``.
- ``--section TEXT`` — Section in the ``.edgerc`` file to use. Useful if you manage multiple
  Akamai accounts in the same credentials file. Defaults to ``default``.

**Config file equivalent:**

.. code-block:: toml

   [main]
   edgerc_path = "~/.edgerc"
   edgerc_section = "default"

Cache
-----

``akcli`` caches API responses by default to avoid unnecessary requests and improve performance.

- ``--cache-dir PATH`` — Custom directory to store cached responses. Defaults to the system cache directory.
- ``--cache-ttl FLOAT`` — Cache expiration time in seconds. Defaults to ``300``.
- ``--use-cache / --no-use-cache`` — Enable or disable response caching. Enabled by default.

**Config file equivalent:**

.. code-block:: toml

   [main]
   cache_dir = "~/.cache"
   cache_ttl = 300
   use_cache = true

.. note::
   If you are expecting updated results after a change but keep getting the same response,
   the cache may be serving a stale result. Disable it temporarily with ``--no-use-cache``
   or refer to :doc:`../troubleshooting` for more details.

Network
-------

- ``--proxy TEXT`` — Proxy server URL to route requests through. Not set by default.
- ``--request-timeout INTEGER`` — Timeout in seconds for API requests, between ``0`` and ``120``. Defaults to ``15``.
- ``--validate-certs / --no-validate-certs`` — Enable or disable SSL certificate validation. Enabled by default.

.. warning::
   Disabling SSL certificate validation exposes your connection to potential security risks.
   Only do this in trusted environments.

**Config file equivalent:**

.. code-block:: toml

   [main]
   proxy = "http://proxy.example.com:8080"
   request_timeout = 15
   validate_certs = true
