[CmdletBinding()]
param([switch]$DryRun=$true)
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot;$lock=Get-VersionLock;$plan=@()
foreach($r in $lock.repositories.psobject.Properties){$plan+=[ordered]@{vendor=$r.Name;current=$r.Value.commit;operation='fetch candidate into temporary worktree; verify; never pull active tree'}}
[ordered]@{status='success';summary='Update dry-run only; no fetch or checkout performed.';next_actions=@('Approve a candidate commit before network access.');artifacts=@("$root\versions.lock");actions=$plan}|ConvertTo-Json -Depth 6
