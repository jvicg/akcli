Translate
=========

Translate an Akamai Error Reference ID into human-readable diagnostic information.
When Akamai serves an error to an end user, it generates a unique reference ID that encodes
details about the request, the edge server, and the failure. This command decodes that ID
and returns the full diagnostic context.

-----------------------------------------------------------------------

Usage
-----

.. code-block:: bash

   akcli translate [OPTIONS] ID

Arguments
---------

- ``ID``
  The Akamai error reference ID to translate. It can usually be found in the error page
  served to the end user, in a format similar to ``11.a1b2c3d4.1234567890.ab12cd3``.

Options
-------

- ``--trace``
  Retrieve logs from all edge servers involved in serving the request. Useful for deeper
  diagnosis of complex failures.

- ``--json``
  Output the result in JSON format.

Configuration
-------------

The following options can be set in the ``[translate]`` section of the config file:

.. code-block:: toml

   ...

   [translate]
   trace = false

Output
------

Results are displayed as a nested table with the full diagnostic context of the error:

.. code-block:: text

   ┌───────────────────────┬─────────────────────────────────────────────┐
   │ Cache Key Hostname    │ example.com                                 │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Client Ip             │ 93.184.216.34                               │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Client Request Method │ GET                                         │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Edge Server Ip        │ 95.101.100.10                               │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Http Response Code    │ 503                                         │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Reason For Failure    │ ERR_DNS_FAIL. The origin server IP address  │
   │                       │ couldn't be resolved.                       │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Property Name         │ example.com                                 │
   ├───────────────────────┼─────────────────────────────────────────────┤
   │ Date                  │ 2026-01-01T00:00:00Z                        │
   └───────────────────────┴─────────────────────────────────────────────┘

Examples
--------

Translate an error reference:

.. code-block:: bash

    akcli translate 11.a1b2c3d4.1234567890.ab12cd3

Translate with trace logs:

.. code-block:: bash

   akcli translate 11.a1b2c3d4.1234567890.ab12cd3 --trace

.. hint::
   If you are using the character ``#`` when decoding an error ID, remember
   to wrap in quotes to prevent the shell from interpreting it as a comment.
