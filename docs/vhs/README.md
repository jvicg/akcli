# vhs

This directory contains [VHS](https://github.com/charmbracelet/vhs) tape scripts used to generate the GIF recordings shown in the documentation.

## Configuration

Global tapes configuration is controlled on `config.tape`.

## Regenerating GIFs

To regenerate a GIF, run:

```bash
vhs <script>.tape
```

Output GIFs are saved directly to `docs/source/_static/`.
