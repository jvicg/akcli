Contributing
============

Thank you for considering contributing to akcli! Any contribution is welcome and appreciated.

.. contents:: Table of Contents
   :local:
   :depth: 1

How can I contribute?
---------------------

Reporting bugs
~~~~~~~~~~~~~~

If you discover a bug, please check the `existing issues <https://github.com/jvicg/akcli/issues>`_
to see if it has already been reported. If not, open a new issue with the following details:

- **Title**: A concise summary of the bug.
- **Description**: Detailed information about the issue, including steps to reproduce, expected
  behavior, and any relevant logs or error messages.

Suggesting enhancements
~~~~~~~~~~~~~~~~~~~~~~~

To propose an enhancement:

1. Check that it hasn't already been suggested in the `existing issues <https://github.com/jvicg/akcli/issues>`_.
2. Open a new issue with a clear title and a detailed explanation of the proposed improvement.

Submitting pull requests
~~~~~~~~~~~~~~~~~~~~~~~~

1. Fork the repository and clone your fork locally.
2. Create a new branch: ``git checkout -b feature/your-feature-name``
3. Make your changes and commit them following the :ref:`commit-messages` guidelines.
4. Push to your fork: ``git push origin feature/your-feature-name``
5. Open a pull request against the original repository with a clear description of your changes.

Style guides
------------

Code style
~~~~~~~~~~

This project follows `PEP 8 <https://peps.python.org/pep-0008/>`_ as the base coding standard,
enforced automatically by `Ruff <https://docs.astral.sh/ruff/>`_. Ruff runs as a pre-commit hook
so most style issues are caught before committing.

Type hints are required for all function signatures.

When adding comments, focus on explaining *why* the code does something rather than *what* it
does. The code itself should be clear enough to convey the what; comments are for capturing
intent, context, or non-obvious decisions that the code alone cannot express.

Pre-commit hooks
~~~~~~~~~~~~~~~~

This project uses `pre-commit <https://pre-commit.com/>`_ to enforce code quality automatically
before each commit and push. Setting it up is required before submitting any pull request.

Install and enable the hooks:

.. code-block:: bash

   pip install pre-commit
   pre-commit install --install-hooks

Once installed, the following checks will run automatically:

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - Stage
     - Hook
     - Description
   * - commit-msg
     - ``conventional-pre-commit``
     - Enforces Conventional Commits format
   * - pre-commit
     - ``trailing-whitespace``
     - Removes trailing whitespace from Python files
   * - pre-commit
     - ``end-of-file-fixer``
     - Ensures all Python files end with a newline
   * - pre-commit
     - ``check-yaml``
     - Validates YAML file syntax
   * - pre-commit
     - ``check-added-large-files``
     - Prevents large files from being committed
   * - pre-commit
     - ``ruff``
     - Runs the linter and formatter
   * - pre-commit
     - ``pytest (unit)``
     - Runs the unit test suite
   * - pre-push
     - ``pytest (full)``
     - Runs the full test suite

.. _commit-messages:

Commit messages
~~~~~~~~~~~~~~~

This project follows the `Conventional Commits <https://www.conventionalcommits.org/>`_ specification.

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Type
     - Title
     - Description
   * - ``feat``
     - Features
     - A new feature
   * - ``fix``
     - Bug Fixes
     - A bug fix
   * - ``docs``
     - Documentation
     - Documentation only changes
   * - ``style``
     - Styles
     - Changes that do not affect the meaning of the code
   * - ``refactor``
     - Code Refactoring
     - A code change that neither fixes a bug nor adds a feature
   * - ``perf``
     - Performance Improvements
     - A code change that improves performance
   * - ``test``
     - Tests
     - Adding missing tests or correcting existing tests
   * - ``build``
     - Builds
     - Changes that affect the build system or external dependencies
   * - ``ci``
     - Continuous Integration
     - Changes to CI configuration files and scripts
   * - ``chore``
     - Chores
     - Other changes that don't modify src or test files
   * - ``revert``
     - Reverts
     - Reverts a previous commit
