---
name: codex-mail-status
description: Use when verifying local worker mail smoke status and writing a user-visible result window.
---

# codex-mail-status

## Purpose

Verify whether the local worker can complete its mail smoke path and report the result without exposing local recipient data or local configuration.

## Rules

- Keep `PHASE_1_SIMULATION_ONLY`.
- Use only local settings already present on the Mac mini.
- Do not write recipient values into repository files.
- Do not print local configuration.
- Report only one of: `LOCAL_WORKER_MAIL_SENT`, `LOCAL_WORKER_MAIL_SKIPPED_NO_RECIPIENT`, `LOCAL_WORKER_MAIL_FAILED`.
- Update `GPT_CODEX_CONVERSATION.md`, `TASK_QUEUE.md`, `STATUS.md`, and `RUN_LOG.md`.
