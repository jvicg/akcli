#!/usr/bin/env bash
# docs/vhs/generate.sh
# Generate all the gifs using the .tapes files located on docs/vhs

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for tape in "$SCRIPT_DIR"/*.tape; do
    [ "$(basename "$tape")" = "config.tape" ] && continue
    echo "Generating $(basename "$tape")..."
    vhs "$tape"
done
