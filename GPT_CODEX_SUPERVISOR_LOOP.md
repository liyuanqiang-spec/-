# GPT-Codex Supervisor Loop

Current mode: `MAC_MINI_LOCAL_WORKER`

Current marker: `LOCAL_WORKER_PRIMARY_ROUTE_READY`

This project uses the Mac mini as the execution agent. ChatGPT supervises by
reading and writing GitHub repository files.

## Flow

```text
ChatGPT writes safe task
-> TASK_QUEUE.md on GitHub
-> Mac mini Codex worker pulls main
-> Codex executes safe repository task
-> Codex writes STATUS.md / RUN_LOG.md / GPT_REVIEW.md / GPT_LOCAL_REVIEW_INPUT.md
-> Codex commits and pushes
-> ChatGPT reads feedback and writes the next task
```

## Timing

| State | Poll interval | Meaning |
|---|---:|---|
| `ACTIVE` | 30s | Pending/running task exists. |
| `WARM` | 60s | Recent activity or blocker exists. |
| `IDLE` | 600s | No pending safe task. |

Night quiet window is `22:00-08:00`. During that window, if no pending task is
detected, the local worker stretches to `WARM=600s` and `IDLE=1800s` to reduce
Mac mini work. Once a pending safe task is detected, execution still uses the
normal active path.

## Visual Surfaces

| File | Reader | Purpose |
|---|---|---|
| `TASK_QUEUE.md` | ChatGPT + Codex | Next task channel. |
| `GPT_VISIBLE_STATUS.md` | ChatGPT + user | Current state summary. |
| `GPT_CODEX_CONVERSATION.md` | user + ChatGPT | Read-only GPT/Codex task and feedback timeline. |
| `WORKER_DASHBOARD.md` | user | Worker health and polling state. |
| `RUN_LOG.md` | ChatGPT + Codex | Execution log. |
| `STATUS.md` | everyone | Durable status history. |
| `GPT_REVIEW.md` | ChatGPT | Codex feedback for review. |
| `GPT_LOCAL_REVIEW_INPUT.md` | ChatGPT | Compact latest handoff packet. |
| `DECISION_REQUIRED.md` | user | Human-only blockers. |

Desktop entry:

- `/Users/zhoujiali/Library/Mobile Documents/com~apple~CloudDocs/Desktop/查看GPT和Codex对话.command`
- It opens a local read-only monitor window and does not execute tasks.

Local health guard:

- Launchd label: `com.codex.github-worker-health-guard`
- Default interval: `900s`
- It checks the worker and restarts it if needed. It does not call models, spend
  tokens, connect trading accounts, or delete data.

## Boundary

`PHASE_1_SIMULATION_ONLY` remains binding.

The loop must not connect to real trading accounts, place or cancel orders,
move funds, expose secrets, delete original/raw data, use `danger-full-access`,
or make large paid API/cloud calls.

## Current Recommendation

Keep the Mac mini on. Use the local worker as the primary route. The hosted
route remains parked for later.
