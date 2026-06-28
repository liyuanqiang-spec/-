# RELIABILITY_RUNBOOK.md

Purpose: keep the ChatGPT -> GitHub -> local Codex worker -> GitHub -> ChatGPT loop visible, recoverable, and safe.

## Operating objective

A safe pending task in `TASK_QUEUE.md` should not silently sit without a visible explanation.

The system must always expose one of four states:

| State | Meaning | Required surface |
|---|---|---|
| `WORKING` | Worker is processing a safe task | `STATUS.md`, `RUN_LOG.md`, `WORKER_DASHBOARD.md` |
| `IDLE` | No pending safe task exists | `WORKER_DASHBOARD.md`, `GPT_VISIBLE_STATUS.md` |
| `WAITING_FOR_WORKER` | A safe task exists but has not been processed yet | `WORKER_DASHBOARD.md`, `GPT_VISIBLE_STATUS.md` |
| `BLOCKED` | A genuine blocker exists | `DECISION_REQUIRED.md`, `WORKER_DASHBOARD.md`, `GPT_VISIBLE_STATUS.md` |

## Source of truth order

1. `TASK_QUEUE.md` tells what should happen next.
2. `STATUS.md` tells the latest durable worker status.
3. `RUN_LOG.md` tells execution history.
4. `DECISION_REQUIRED.md` tells only unresolved human blockers.
5. `WORKER_DASHBOARD.md` is the user-facing summary.
6. `GPT_VISIBLE_STATUS.md` is the GPT-facing summary page.

## Reliability rules

1. Stale blocker entries must not keep the dashboard in `ATTENTION` if later worker output proves progress resumed.
2. A pending safe task must be visible as `WAITING_FOR_WORKER`, not hidden behind old blocker text.
3. The worker should refresh `WORKER_DASHBOARD.md` whenever it completes, blocks, or detects a pending safe task that it cannot process.
4. ChatGPT hourly status checks must read the six status files and report exact unavailable files, not infer missing data.
5. Repository-maintenance tasks must remain inside the repository and must not require machine-level configuration changes.
6. If a Git sync problem occurs, the worker should record the exact command stage: `pull`, `push`, `commit`, or `status refresh`.

## Standard recovery flow

### Case A: queue has pending task but dashboard says no current task

Action:

1. Refresh `WORKER_DASHBOARD.md` from `TASK_QUEUE.md`, `STATUS.md`, `RUN_LOG.md`, and `DECISION_REQUIRED.md`.
2. Mark state as `WAITING_FOR_WORKER`.
3. Show the first pending task ID and title.
4. Do not ask the user unless the pending task is unsafe or requires external access.

### Case B: old `git pull failed` entries remain visible after later completion

Action:

1. Keep those entries in history.
2. Mark them resolved in `DECISION_REQUIRED.md`.
3. Regenerate `WORKER_DASHBOARD.md` so `DECISION_REQUIRED blocking` becomes `No`.
4. Write the reason in `GPT_VISIBLE_STATUS.md`.

### Case C: worker has not pushed new output after a pending safe task appears

Action:

1. ChatGPT records `WAITING_FOR_WORKER` in `GPT_VISIBLE_STATUS.md`.
2. Keep hourly checking active.
3. Append or rewrite the next queue item as a safe repository-status recovery task.
4. Avoid broad task wording that can trip risk control.

## Permanent process

Every hourly status check should output five fields:

1. Worker state.
2. First pending task.
3. Latest completed task.
4. Genuine unresolved blocker, if any.
5. Next recommended action.

The next recommended action should be executable by Codex whenever possible, not pushed back to the user.
