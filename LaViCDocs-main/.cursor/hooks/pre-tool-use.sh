#!/bin/bash
# planning-with-files: Pre-tool-use hook for Cursor
# Reads the first 30 lines of task_plan.md to keep goals in context.
# Returns {"decision": "allow"} — this hook never blocks tools.

SKILL_FILE="AIAgentData/skill/skill.md"
PLAN_FILE="task_plan.md"

if [ ! -f "$SKILL_FILE" ]; then
    echo '{"decision": "block", "reason": "Missing AIAgentData/skill/skill.md"}'
    exit 1
fi

echo "【强制前置】执行任何工具前必须阅读并遵循 AIAgentData/skill/skill.md" >&2
cat "$SKILL_FILE" >&2

if [ -f "$PLAN_FILE" ]; then
    head -30 "$PLAN_FILE" >&2
fi

echo '{"decision": "allow"}'
exit 0
