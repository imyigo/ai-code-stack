#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
if command -v pwsh >/dev/null 2>&1; then PS=pwsh; elif command -v powershell.exe >/dev/null 2>&1; then PS=powershell.exe; else echo 'PowerShell is required.' >&2; exit 2; fi
exec "$PS" -NoProfile -ExecutionPolicy Bypass -File "$ROOT/scripts/verify.ps1" "$@"
