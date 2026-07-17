Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-StackRoot { Split-Path -Parent $PSScriptRoot }
function Get-VersionLock { Get-Content -Raw -LiteralPath (Join-Path (Get-StackRoot) 'versions.lock') | ConvertFrom-Json }
function Get-CommandPath([string]$Name) { (Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -First 1).Source }
function Get-Sha256([string]$Path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant() }
function Assert-ChildPath([string]$Parent,[string]$Child) {
  $p=[IO.Path]::GetFullPath($Parent).TrimEnd('\')+'\'; $c=[IO.Path]::GetFullPath($Child)
  if(-not $c.StartsWith($p,[StringComparison]::OrdinalIgnoreCase)){ throw "Unsafe path outside $Parent`: $Child" }
}
function New-Result([string]$Status,[string]$Summary,[string[]]$Next=@(),[string[]]$Artifacts=@()) {
  [ordered]@{status=$Status;summary=$Summary;next_actions=$Next;artifacts=$Artifacts}
}
