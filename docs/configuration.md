# Configuration

`akcli` can be configured via a config file in TOML format. To generate a config file with the default values run:

```bash
akcli --init-config-file
```

!!! tip
    The config file is generated at `~/.config/akcli/config.toml`. You can edit it manually at any time.

## Options

### Main

| Option            | Default          | Description                            |
| ----------------- | ---------------- | -------------------------------------- |
| `edgerc_path`     | `~/.edgerc`      | Path to the EdgeGrid credentials file. |
| `edgerc_section`  | `default`        | Section to use from the EdgeGrid file. |
| `cache_dir`       | System cache dir | Directory to store cached responses.   |
| `cache_ttl`       | `300`            | Cache TTL in seconds.                  |
| `use_cache`       | `true`           | Enable or disable caching.             |
| `request_timeout` | `15`             | Request timeout in seconds.            |
| `validate_certs`  | `true`           | Validate SSL certificates.             |
| `proxy`           | —                | Proxy URL.                             |

### dig

| Option         | Default | Description            |
| -------------- | ------- | ---------------------- |
| `query_type`   | `A`     | DNS query type.        |
| `raw`          | `false` | Show raw API response. |
| `short_output` | `false` | Show short output.     |

### translate

| Option  | Default | Description                |
| ------- | ------- | -------------------------- |
| `trace` | `false` | Enable trace forward logs. |

## Example

```toml
[main]
edgerc_section = "production"
request_timeout = 30

[dig]
query_type = "AAAA"
short_output = true
```

!!! warning
    Unknown sections or options in the config file are ignored with a warning. Check the option names carefully if a value is not being applied.
