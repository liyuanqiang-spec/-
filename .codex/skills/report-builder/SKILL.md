---
name: report-builder
description: Use when turning test results, task results, or research findings into readable Markdown reports.
---

# report-builder

## Purpose

Create concise reports that tell the user what changed, what passed, what failed, and what to do next.

## Report structure

1. Current status.
2. What was done.
3. Evidence or metrics.
4. Blockers if any.
5. Next safe action.

## Rules

- Prefer short tables.
- Put detailed logs in `RUN_LOG.md`.
- Put user-facing summary in `REPORTS/` or `GPT_CODEX_CONVERSATION.md`.
- Avoid unexplained technical noise.
