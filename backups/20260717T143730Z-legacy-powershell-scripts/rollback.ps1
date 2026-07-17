[CmdletBinding(SupportsShouldProcess)]
param([Parameter(Mandatory)][string]$BackupPath)
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot;$manifest=Join-Path $BackupPath 'backup-manifest.json'
if(!(Test-Path $manifest)){throw "Backup manifest missing: $manifest"}
if($PSCmdlet.ShouldProcess($root,'restore AI Code Stack baseline')){
  Copy-Item -Force "$BackupPath\repo-baseline\README.md" "$root\README.md"
  Copy-Item -Force "$BackupPath\repo-baseline\versions.lock" "$root\versions.lock"
  Copy-Item -Force "$BackupPath\repo-baseline\install.sh" "$root\install.sh"
  Copy-Item -Force "$BackupPath\repo-baseline\verify.sh" "$root\verify.sh"
  Copy-Item -Recurse -Force "$BackupPath\repo-baseline\config" $root
  Copy-Item -Force "$BackupPath\global-config\config.toml" "$HOME\.codex\config.toml"
  Copy-Item -Force "$BackupPath\global-config\AGENTS.md" "$HOME\.codex\AGENTS.md"
  New-Result success 'Baseline files restored. Restart platform applications and run the baseline verifier.' @() @($BackupPath)
}
