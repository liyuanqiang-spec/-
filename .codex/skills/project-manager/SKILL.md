---
name: project-manager
description: Use for planning, task tracking, status updates, milestone control, and A/B/C decision prompts.
---

# Project Manager Skill

Use this skill at the start and end of each project phase.

## Rules

1. Every development task starts with a plan.
2. Every completed phase updates `STATUS.md`.
3. On errors, attempt three automatic repair rounds before asking the user.
4. When user decision is required, present exactly A/B/C options and recommend one.
5. End every task with completed work, files changed, tests, current issues, next step, and whether confirmation is required.

## Output

- Plan
- Phase status
- Decision options
- Completion report
