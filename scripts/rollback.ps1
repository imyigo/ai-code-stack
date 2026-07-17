# Thin wrapper: delegates to the canonical Python rollback. Contains no business logic.
[CmdletBinding(SupportsShouldProcess)]
param([Parameter(Mandatory)][string]$BackupPath)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) { throw 'Python 3 is required.' }
if ($PSCmdlet.ShouldProcess($root, 'restore AI Code Stack from backup')) {
  & $py.Source (Join-Path $root 'scripts\rollback.py') --root $root --backup $BackupPath
  exit $LASTEXITCODE
}
