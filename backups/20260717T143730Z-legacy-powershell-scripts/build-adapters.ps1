[CmdletBinding()]
param([switch]$Check)
. "$PSScriptRoot\Common.ps1"
$root=Get-StackRoot;$required=@('orchestration\ORCHESTRATION.md','orchestration\ROUTING.md','orchestration\SECURITY.md','orchestration\RELEASE-GATE.md','orchestration\PRECEDENCE.md')
$missing=@($required|Where-Object{!(Test-Path (Join-Path $root $_))});if($missing){throw "Canonical sources missing: $missing"}
$generated=@('adapters\codex\AGENTS.md','adapters\claude-code\CLAUDE.md','adapters\cursor\AI-CODE-STACK.mdc')
$bad=@($generated|Where-Object{!(Select-String -Quiet (Join-Path $root $_) 'GENERATED')});if($bad){throw "Generated marker missing: $bad"}
New-Result success 'Adapter sources and generated markers verified.' @() ($generated|ForEach-Object{Join-Path $root $_})
