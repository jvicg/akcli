# translate

Translate an Akamai Error String.

## Usage

```bash
akcli translate [OPTIONS] ERROR_CODE
```

## Arguments

| Argument     | Description                     |
| ------------ | ------------------------------- |
| `ERROR_CODE` | Akamai error code to translate. |

## Options

| Option    | Default | Description                |
| --------- | ------- | -------------------------- |
| `--trace` | `false` | Enable trace forward logs. |

## Examples

```bash
akcli translate 9.6f3a3d4.1234567890.1a2b3c4
akcli translate 9.6f3a3d4.1234567890.1a2b3c4 --trace
```
