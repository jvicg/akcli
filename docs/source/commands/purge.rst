Purge
=====

Purge one or more objects from the Akamai network using the Fast Purge API. Supports
invalidation and deletion of URLs/ARLs, CP codes and cache tags, on both staging and
production networks.

-----------------------------------------------------------------------

Usage
-----

.. code-block:: bash

   akcli purge [OPTIONS] [OBJECTS]...

Arguments
---------

- ``OBJECTS``
  One or more objects to purge (URLs/ARLs, CP codes or cache tags). Mutually exclusive
  with ``--from-file``.

Options
-------

- ``--method [invalidate|delete]``
  Purge method. ``invalidate`` marks content as stale and lets Akamai re-fetch it on the
  next request. ``delete`` removes the object from cache entirely. Defaults to ``invalidate``.

- ``--purge-type [url|cpcode|tag]``
  Type of objects to purge. Defaults to ``url``.

- ``--network [staging|production]``
  Akamai network to purge from. Defaults to ``staging``.

- ``--from-file PATH``
  Path to a plain text file with one object per line. Empty lines and leading/trailing
  whitespace are ignored. Mutually exclusive with positional ``OBJECTS``.

- ``--json``
  Output the result in JSON format, as returned by the Akamai API without parsing.

.. note::
   Note that cache is disabled for this command — every invocation always reaches the API,
   since purge is a write operation and caching would silently skip the actual request.

Config file
-----------

The following options can be set in the ``[purge]`` section of the config file:

.. code-block:: toml

   ...
   [purge]
   method = "invalidate"
   type = "url"
   network = "staging"

Output
------

By default, a success message is shown with the purge ID and the estimated completion time:

.. image:: /_static/purge.gif
   :alt: Output of `akcli purge https://example.com/image.jpg`
   :class: command-output

Examples
--------

Invalidate a URL on staging:

.. code-block:: bash

   akcli purge https://example.com/image.jpg

Delete a URL from production:

.. code-block:: bash

   akcli purge https://example.com/image.jpg --method delete --network production

Purge by CP code:

.. code-block:: bash

   akcli purge 123456 --purge-type cpcode

Purge multiple cache tags at once:

.. code-block:: bash

   akcli purge tag-1 tag-2 tag-3 --purge-type tag

Bulk purge from a file:

.. code-block:: bash

   akcli purge --from-file urls.txt --purge-type url --network production
