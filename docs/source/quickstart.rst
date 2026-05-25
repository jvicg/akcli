Quick start
===========

Before using ``akcli``, you need a valid EdgeGrid credentials file ``.edgerc`` to authenticate
with Akamai's API. Follow the official `EdgeGrid authentication guide
<https://techdocs.akamai.com/developer/docs/edgegrid>`_ to set it up.

Configuration file
------------------

``akcli`` works out of the box with sensible defaults and only requires a valid ``.edgerc`` file.

Optionally, you can generate a config file to persist your preferred defaults:

.. code-block:: bash

   akcli --init-config-file

This creates a TOML config file at the following path depending on your operating system:

- **Linux/macOS:** ``~/.config/akcli/config.toml``
- **Windows:** ``%APPDATA%\akcli\config.toml``

In this file you can set your preferred defaults — edgerc path, cache settings, timeouts, and
more — so you never have to pass the same flags repeatedly. See :doc:`commands/index`
for the full reference.

.. note::
   Command line flags take priority over configuration file parameters.
   You can use configuration file to set your most used options and overwrite them at
   any time using the cli flags.


Examples
--------

Explore all available commands:

.. code-block:: bash

   akcli --help

Resolve a domain and get only the returned values:

.. code-block:: bash

   akcli dig example.com --short

Query a specific DNS record type:

.. code-block:: bash

   akcli dig example.com --query-type MX

Translate an Akamai error reference ID:

.. code-block:: bash

   akcli translate 11.a1b2c3d4.1234567890.ab12cd3

Use a non-default EdgeGrid section, custom `.edgerc` file and disable caching to ensure a fresh response:

.. code-block:: bash

   akcli --section staging --edgerc /custom/path/.edgerc --no-use-cache dig example.com

Route requests through a proxy with a custom timeout:

.. code-block:: bash

   akcli --proxy http://proxy.example.com:8080 --request-timeout 30 dig example.com

Disable SSL validation in a controlled environment:

.. code-block:: bash

   akcli --no-validate-certs dig example.com
