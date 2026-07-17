[CmdletBinding(SupportsShouldProcess)]
param([switch]$DryRun,[switch]$VerboseReport)
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot;$lock=Get-VersionLock;$actions=[Collections.Generic.List[object]]::new()
foreach($r in $lock.repositories.psobject.Properties){$path=Join-Path $root "vendors\$($r.Name)";$actions.Add([ordered]@{action='verify_vendor';path=$path;commit=$r.Value.commit;exists=(Test-Path "$path\.git")})}
$actions.Add([ordered]@{action='build_adapters';source="$root\orchestration";target="$root\adapters"})
$actions.Add([ordered]@{action='link_skills';strategy='junction_then_symlink_then_controlled_copy';target='C:\WyvOS\skills'})
$actions.Add([ordered]@{action='merge_mcp';platforms=@('codex','claude-code','cursor');antigravity='skip-unverified'})
$actions.Add([ordered]@{action='verify';command="$PSScriptRoot\verify.ps1"})
if($DryRun){New-Result success 'Dry-run only; no state changed.' @('Review actions, then rerun without -DryRun.') @($root)|ForEach-Object{$_['actions']=$actions;$_}|ConvertTo-Json -Depth 8;exit 0}
$missing=@($actions|Where-Object{$_.action -eq 'verify_vendor' -and !$_.exists});if($missing){throw 'Vendor submodules are missing. Run git submodule update --init --recursive after approval.'}
& "$PSScriptRoot\build-adapters.ps1"
& "$PSScriptRoot\link-skills.ps1" -DryRun
& "$PSScriptRoot\verify.ps1"
New-Result success 'Install validation completed. Skill relink remains preview-only until its manifest is approved.' @('Review link dry-run before atomic activation.') @($root)
