#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORGEWEB_DIR="$ROOT_DIR/ForgeWeb"

if [[ ! -d "$FORGEWEB_DIR/admin" ]]; then
  echo "ForgeWeb submodule is missing. Run: git submodule update --init --recursive" >&2
  exit 1
fi

cd "$FORGEWEB_DIR"
export WEBSITE_ROOT="${WEBSITE_ROOT:-..}"
exec python3 admin/file-api.py "$@"
