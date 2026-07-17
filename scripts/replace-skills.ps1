# Thin wrapper: delegates to the canonical Python installer. Contains no business logic.
[CmdletBinding(SupportsShouldProcess)]
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) { throw 'Python 3 is required.' }
$extraArgs = @()
if ($Apply) { $extraArgs += '--apply' }
& $py.Source (Join-Path $root 'scripts\replace_skills.py') --root $root @extraArgs
exit $LASTEXITCODE
