[CmdletBinding(SupportsShouldProcess)]
param([switch]$DryRun,[string]$Target='C:\WyvOS\skills')
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot;$manifest="$root\manifests\skills.json";if(!(Test-Path $manifest)){throw "Skill manifest missing: $manifest"}
$skills=Get-Content -Raw $manifest|ConvertFrom-Json;$plan=@($skills.skills|ForEach-Object{[ordered]@{name=$_.active_name;source=$_.source_path;target=(Join-Path $Target $_.folder);mode=$_.activation_mode}})
if($DryRun){[ordered]@{status='success';summary='Skill link dry-run; no state changed.';next_actions=@('Approve atomic activation after reviewing collisions.');artifacts=@($manifest);actions=$plan}|ConvertTo-Json -Depth 6;exit 0}
throw 'Atomic live activation is intentionally gated. Run -DryRun and approve its manifest before enabling.'
