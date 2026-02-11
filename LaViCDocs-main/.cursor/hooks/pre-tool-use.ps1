# planning-with-files: Pre-tool-use hook for Cursor (PowerShell)
# Reads the first 30 lines of task_plan.md to keep goals in context.
# Returns {"decision": "allow"} — this hook never blocks tools.

$SkillFile = "AIAgentData/skill/skill.md"
$PlanFile = "task_plan.md"

if (-not (Test-Path $SkillFile)) {
    Write-Output '{"decision": "block", "reason": "Missing AIAgentData/skill/skill.md"}'
    exit 1
}

Write-Host "【强制前置】执行任何工具前必须阅读并遵循 AIAgentData/skill/skill.md"
Get-Content $SkillFile | Write-Host

if (Test-Path $PlanFile) {
    Get-Content $PlanFile -TotalCount 30 | Write-Host
}

Write-Output '{"decision": "allow"}'
exit 0
