[CmdletBinding()]
param([switch]$Json,[switch]$IncludeStartupTest)
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot; $lock=Get-VersionLock; $checks=[Collections.Generic.List[object]]::new()
function Check($Name,[scriptblock]$Test,[string]$Evidence){try{$ok=&$Test;$checks.Add([ordered]@{name=$Name;status=if($ok){'pass'}else{'fail'};evidence=$Evidence})}catch{$checks.Add([ordered]@{name=$Name;status='fail';evidence=$_.Exception.Message})}}
Check 'version_manifest_parse' {$lock.schema_version -eq 'ai-code-stack.2'} "$root\versions.lock"
Check 'git_repository' {Test-Path "$root\.git"} $root
Check 'submodule_manifest' {Test-Path "$root\.gitmodules"} "$root\.gitmodules"
Check 'canonical_orchestration' {@('ORCHESTRATION','ROUTING','SECURITY','RELEASE-GATE','PRECEDENCE','PLATFORM-CAPABILITIES')|ForEach-Object{if(!(Test-Path "$root\orchestration\$_.md")){return $false}};$true} "$root\orchestration"
Check 'graphify_cli' {(& graphify --version 2>$null) -match [regex]::Escape($lock.runtimes.graphify_cli)} (Get-CommandPath graphify)
Check 'graphify_mcp_binary' {[bool](Get-CommandPath graphify-mcp)} (Get-CommandPath graphify-mcp)
Check 'codex_graphify_mcp' {(Get-Content -Raw "$HOME\.codex\config.toml") -match '\[mcp_servers\.graphify\]'} "$HOME\.codex\config.toml"
Check 'skill_count' {@(Get-ChildItem 'C:\WyvOS\skills' -Directory).Count -eq $lock.expected_active_skills} 'C:\WyvOS\skills'
Check 'skill_frontmatter' {$bad=@(Get-ChildItem 'C:\WyvOS\skills' -Directory|Where-Object{!(Test-Path "$($_.FullName)\SKILL.md") -or !(Select-String -Quiet "$($_.FullName)\SKILL.md" '^name:\s*\S+')});$bad.Count -eq 0} 'C:\WyvOS\skills'
Check 'skill_unique_names' {$n=@(Get-ChildItem 'C:\WyvOS\skills' -Directory|ForEach-Object{(Select-String "$($_.FullName)\SKILL.md" '^name:\s*(.+)$').Matches.Groups[1].Value.Trim()});(@($n|Group-Object|Where-Object Count -gt 1).Count -eq 0)} 'frontmatter names'
Check 'broken_links' {@(Get-ChildItem 'C:\WyvOS\skills' -Directory|Where-Object{$_.LinkType -and !(Test-Path $_.FullName)}).Count -eq 0} 'active skill links'
Check 'benchmark_alias_manifest' {(Get-Content -Raw "$root\overlays\shared\aliases.json") -match 'gstack-benchmark'} "$root\overlays\shared\aliases.json"
Check 'security_gate' {Test-Path "$root\config\security-release-gate.sh"} "$root\config\security-release-gate.sh"
Check 'no_vendor_policy_edits' {@(git -C $root submodule foreach --quiet 'git status --porcelain' 2>$null|Where-Object{$_}).Count -eq 0} 'vendor worktrees'
$failed=@($checks|Where-Object status -eq 'fail').Count;$result=[ordered]@{status=if($failed){'error'}else{'success'};summary="$($checks.Count-$failed) passed, $failed failed";next_actions=if($failed){@('Fix failed checks; do not install or ship.')}else{@('Safe to continue to the next gated stage.')};artifacts=@("$root\versions.lock");checks=$checks}
if($Json){$result|ConvertTo-Json -Depth 6}else{$checks|Format-Table -AutoSize;"SUMMARY $($result.summary)"}
if($failed){exit 1}
