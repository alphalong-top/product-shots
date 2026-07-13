#!/usr/bin/env bash
# Run the optional API client from its isolated environment.

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR=${PRODUCT_SHOTS_VENV:-${XDG_CACHE_HOME:-$HOME/.cache}/product-shots/venv}
PYTHON="$VENV_DIR/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: API-mode environment missing. Run $SCRIPT_DIR/setup.sh first." >&2
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/generate.py" "$@"
