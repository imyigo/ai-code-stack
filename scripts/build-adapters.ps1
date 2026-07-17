# Thin wrapper: delegates to the canonical Python adapter builder. Contains no business logic.
[CmdletBinding()]
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) { throw 'Python 3 is required.' }
$extraArgs = @()
if ($DryRun) { $extraArgs += '--dry-run' }
& $py.Source (Join-Path $root 'scripts\build_adapters.py') --root $root @extraArgs
exit $LASTEXITCODE
