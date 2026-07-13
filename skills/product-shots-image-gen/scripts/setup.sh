#!/usr/bin/env bash
# Install optional API-mode dependencies into an isolated virtual environment.

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SKILL_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)
VENV_DIR=${PRODUCT_SHOTS_VENV:-${XDG_CACHE_HOME:-$HOME/.cache}/product-shots/venv}

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found. Install Python 3.10+ first." >&2
    exit 1
fi

python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check \
    --requirement "$SKILL_DIR/requirements.txt"

echo "[image-gen] optional API environment ready: $VENV_DIR"
echo "[image-gen] run with: $SCRIPT_DIR/run.sh --help"
