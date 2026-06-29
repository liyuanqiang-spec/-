---
name: github-task-runner
description: Use when receiving GPT-created tasks from TASK_QUEUE.md and returning concise task results.
---

# github-task-runner

## Purpose

Read `TASK_QUEUE.md`, select the first safe pending task, execute repository-local work, and write a clear result back to the queue and visible status files.

## Rules

- Do not repeat completed tasks.
- Prefer the first pending safe task.
- If blocked, mark `decision_required` and give a short reason.
- If completed, mark `completed` and summarize the result.
- Keep task output concise and user-readable.
- Refresh `GPT_CODEX_CONVERSATION.md`, `GPT_VISIBLE_STATUS.md`, `WORKER_DASHBOARD.md`, `STATUS.md`, and `RUN_LOG.md` when relevant.
