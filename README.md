# akcli

[![Pactester latest version](https://img.shields.io/pypi/v/akcli.svg)](https://pypi.org/project/akcli/)
[![CI tests status](https://github.com/jvicg/akcli/actions/workflows/tests.yml/badge.svg)](https://github.com/jvicg/akcli/actions/workflows/tests.yml)
[![Current available Python versions](https://img.shields.io/pypi/pyversions/akcli.svg)](https://pypi.org/project/akcli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](jvicg/akcli/blob/main/LICENSE)

A modern command-line interface for interacting with Akamai's API.

Built for engineers who work with Akamai on a daily basis, `akcli` removes the friction of
working with Akamai's API directly. It exposes a set of commands to interact with different
Akamai API endpoints, providing a fast and intuitive way to work with the platform without
leaving the terminal.

![akcli demo gif](https://raw.githubusercontent.com/jvicg/akcli/main/docs/source/_static/demo.gif)

## Features

- Transparent EdgeGrid authentication — just point `akcli` to your `.edgerc` file and it handles the rest.
- Response caching to avoid hitting the API unnecessarily, with configurable TTL and cache directory.
- Proxy support to route requests through an HTTP/HTTPS proxy with a single config option.
- SSL certificate validation enabled by default, with the option to disable it for internal or development environments.
- TOML config file to persist your preferred defaults and never repeat the same flags.
- Visually modern CLI experience built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/).

## Installation

Requires Python 3.9 or higher and a valid Akamai `.edgerc` credentials file.

```bash
pip install akcli
```

Alternatively, you may download the wheel file from the
[releases page](https://github.com/jvicg/akcli/releases).

## Quick start

Generate a config file with all the default values:

```bash
akcli --init-config-file
```

Explore the available commands:

```bash
akcli --help
```

Resolve a domain using Akamai's Edge servers:

```bash
akcli dig example.com
```

Translate an Akamai error reference:

```bash
akcli translate "11.a1b2c3d4.1234567890.ab12cd3"
```

## Documentation

Full documentation is available on [Read the Docs](https://akcli.readthedocs.io).

## License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this software under the terms of the license.
See the [LICENSE](https://github.com/jvicg/akcli/blob/main/LICENSE) file for full details.
