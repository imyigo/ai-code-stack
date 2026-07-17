#!/usr/bin/env bash
# Thin wrapper: delegates to the canonical Python installer. Contains no business logic.
set -euo pipefail
ROOT="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
PY="$(command -v python3 || command -v python || true)"
if [[ -z "$PY" ]]; then echo 'Python 3 is required.' >&2; exit 2; fi
exec "$PY" "$ROOT/scripts/global_install.py" --root "$ROOT" "$@"
