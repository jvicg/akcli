# dig

Run a `dig` command using an Akamai Edge server.

## Usage

```bash
akcli dig [OPTIONS] HOSTNAME
```

## Arguments

| Argument   | Description        |
| ---------- | ------------------ |
| `HOSTNAME` | Hostname to query. |

## Options

| Option         | Default | Description                             |
| -------------- | ------- | --------------------------------------- |
| `--query-type` | `A`     | DNS query type (A, AAAA, CNAME, MX...). |
| `--raw`        | `false` | Show raw API response.                  |
| `--short`      | `false` | Show short output.                      |

## Examples

```bash
akcli dig example.com
akcli dig example.com --query-type AAAA
akcli dig example.com --short
```

!!! note "Note title"
    This command requires valid Akamai credentials in your `.edgerc` file. See [Configuration](../configuration.md) for details.

!!! warning "Warning title"
    Results are cached by default. If you need a fresh result, disable the cache with `--no-cache`.
