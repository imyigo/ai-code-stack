# Thin wrapper: delegates to the canonical Python verifier. Contains no business logic.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) { throw 'Python 3 is required.' }
& $py.Source (Join-Path $root 'scripts\verify.py') --root $root
exit $LASTEXITCODE
