Dig
===

Resolve domain FQDNs using Akamai's Edge Diagnostics API. The query is executed from an
Akamai Edge server, so the results reflect what Akamai sees — not your local DNS resolver.

-----------------------------------------------------------------------

Usage
-----

.. code-block:: bash

   akcli dig [OPTIONS] HOSTNAME

Arguments
---------

- ``HOSTNAME``
  The fully qualified domain name to query.

Options
-------

- ``--query-type [A|AAAA|SOA|CNAME|PTR|NS|TXT|MX|SRV|CAA|ANY]``
  DNS record type to query. Defaults to ``A``.

- ``--raw``
  Print the raw ``dig``-style response, equivalent to running a standard ``dig`` command locally.

- ``--short``
  Show only the returned values, without the full DNS record details.

- ``--json``
  Output the result in JSON format. Just as returned by the Akamai's API without parsing.

Config file
-----------

The following options can be set in the ``[dig]`` section of the config file:

.. code-block:: toml

   ...

   [dig]
   query_type = "A"
   raw = false
   short_output = false


Output
------

By default, results are displayed as a table with the following columns:

.. image:: /_static/dig.gif
   :alt: Output of `akcli dig example.com`
   :class: command-output

With ``--short``, only the resolved values are shown:

.. image:: /_static/dig-short.gif
   :alt: Output of `akcli dig --short example.com`
   :class: command-output

With ``--raw``, the output mirrors a standard ``dig`` response:

.. image:: /_static/dig-raw.gif
   :alt: Output of `akcli dig --raw example.com`
   :class: command-output


Examples
--------

Basic A record query:

.. code-block:: bash

   akcli dig example.com

Query a specific record type:

.. code-block:: bash

   akcli dig example.com --query-type MX

Show only the returned values:

.. code-block:: bash

   akcli dig example.com --short

Print the raw dig-style response:

.. code-block:: bash

   akcli dig example.com --raw
