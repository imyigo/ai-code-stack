[CmdletBinding()]
param([string]$OutputPath)
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot;if(!$OutputPath){$OutputPath=Join-Path $root 'manifests\last-report.json'}
$report=[ordered]@{schema_version=1;generated_at=(Get-Date).ToString('o');repository=(git -C $root status --short);platforms=(Get-Content -Raw "$root\manifests\platforms.json"|ConvertFrom-Json);links=(Get-Content -Raw "$root\manifests\links.json"|ConvertFrom-Json)}
$report|ConvertTo-Json -Depth 8|Set-Content -Encoding utf8 $OutputPath
New-Result success 'Report exported.' @() @($OutputPath)
