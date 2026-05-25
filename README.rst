akcli
=====
Release |version|.

.. image:: https://img.shields.io/pypi/v/pactester.svg
    :target: https://pypi.org/project/pactester/
    :alt: Pactester latest version
.. image:: https://github.com/jvicg/pactester/actions/workflows/test.yml/badge.svg
    :target: https://github.com/jvicg/pactester
    :alt: CI tests status
.. image:: https://img.shields.io/pypi/pyversions/pactester.svg
    :target: https://pypi.org/project/pactester/
    :alt: Current available Python versions
.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://github.com/jvicg/akcli/blob/main/LICENSE
    :alt: License: MIT

A modern command-line interface for interacting with Akamai's API.

Built for engineers who work with Akamai on a daily basis, ``akcli`` removes the friction of
working with Akamai's API directly. It exposes a set of commands to interact with different Akamai API endpoints,
providing a fast and intuitive way to work with the platform without leaving the terminal.

-----------------------------------------------------------------------

Installation
------------

``akcli`` can be installed using pip:

.. code-block:: bash

   pip install akcli

Alternatively, you may download the wheel file from the
`releases page <https://github.com/jvicg/akcli/releases>`_.

Requirements
------------

- Python 3.9 or higher
- A valid Akamai ``.edgerc`` credentials file

Features
--------

- Transparent EdgeGrid authentication — just point ``akcli`` to your ``.edgerc`` file and it handles the rest.
- Response caching to avoid hitting the API unnecessarily, with configurable TTL and cache directory.
- Proxy support to route requests through an HTTP/HTTPS proxy with a single config option.
- SSL certificate validation enabled by default, with the option to disable it for internal or development environments.
- TOML config file to persist your preferred defaults and never repeat the same flags.
- Provides a visually moder CLI experience built with `Typer <https://typer.tiangolo.com/>`_ and `Rich <https://rich.readthedocs.io/>`_.

License
-------

This project is licensed under the MIT License.
You are free to use, modify, and distribute this software under the terms of the license.
See the `LICENSE <https://github.com/jvicg/akcli/blob/main/LICENSE>`_ file for full details.
