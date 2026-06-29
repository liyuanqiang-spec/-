# GPT Codex Communication Protocol

Generated: 2026-06-29

## Purpose

Make GPT and the local Codex worker cooperate as a software team rather than as one-off task messages.

## Division of labor

| Role | Responsibility |
|---|---|
| GPT | Product direction, architecture, task splitting, acceptance criteria, review, user-facing summary |
| Codex worker | Local execution, file edits, test runs, environment checks, status refresh, result reporting |
| GitHub repo | Task queue, shared memory, status window, reports, evidence log |

## Standard loop

1. User gives goal to GPT.
2. GPT writes a safe task to `TASK_QUEUE.md`.
3. Codex worker picks the first safe pending task.
4. Codex executes locally and updates repo files.
5. GPT reads result and decides pass, fix, or next task.
6. User sees only concise status unless detailed logs are needed.

## Files

| File | Purpose |
|---|---|
| `TASK_QUEUE.md` | Current executable tasks |
| `CODEX_GROUP_CHAT.md` | Multi-role conversation window |
| `GPT_CODEX_CONVERSATION.md` | User-visible GPT/Codex progress |
| `PROJECT_SKILL_REGISTRY.md` | Installed project skills |
| `RUN_LOG.md` | Technical event history |
| `STATUS.md` | Current machine-readable project status |
| `REPORTS/` | Longer reports and reviews |

## Message format

Every meaningful exchange should use this pattern:

```text
[time] [role] [task] [status]
message
```

Allowed status values:

- DONE
- RUNNING
- BLOCKED
- FAILED
- NEEDS_FIX
- SENT
- SKIPPED
- SUCCESS

## Multi-Codex mode

Logical workers may be represented as:

- Codex-Core
- Codex-Quant
- Codex-Data
- Codex-Docs
- Codex-UI
- Codex-Review

If only one real local worker exists, it can simulate these roles by writing role-tagged messages. If multiple real workers exist later, each worker should have a stable `worker_id` and only take tasks assigned to that id or role.

## Safety

Default mode is `PHASE_1_SIMULATION_ONLY`.

No live trading, no fund movement, no destructive cleanup, and no private configuration exposure without separate explicit authorization.
