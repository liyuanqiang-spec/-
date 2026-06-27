---
name: code-review
description: Use for reviewing project code with emphasis on correctness, safety, tests, data handling, and trading-risk boundaries.
---

# Code Review Skill

Use this skill for code review and quality checks.

## Rules

1. Lead with bugs, risks, and missing tests.
2. Check whether code can accidentally trade live or delete important data.
3. Verify tests or explain why tests could not run.
4. Keep refactors scoped and avoid unrelated churn.
5. Update `TASKS.md` or `STATUS.md` when review creates follow-up work.

## Output

- Findings by severity
- Test gaps
- Required fixes
- Safe-to-merge status
