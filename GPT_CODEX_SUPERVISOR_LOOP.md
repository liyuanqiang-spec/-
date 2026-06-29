# GPT-Codex Supervisor Loop

Current mode: `MAC_MINI_LOCAL_WORKER`

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

## Visual Surfaces

| File | Reader | Purpose |
|---|---|---|
| `TASK_QUEUE.md` | ChatGPT + Codex | Next task channel. |
| `GPT_VISIBLE_STATUS.md` | ChatGPT + user | Current state summary. |
| `WORKER_DASHBOARD.md` | user | Worker health and polling state. |
| `RUN_LOG.md` | ChatGPT + Codex | Execution log. |
| `STATUS.md` | everyone | Durable status history. |
| `GPT_REVIEW.md` | ChatGPT | Codex feedback for review. |
| `GPT_LOCAL_REVIEW_INPUT.md` | ChatGPT | Compact latest handoff packet. |
| `DECISION_REQUIRED.md` | user | Human-only blockers. |

## Boundary

`PHASE_1_SIMULATION_ONLY` remains binding.

The loop must not connect to real trading accounts, place or cancel orders,
move funds, expose secrets, delete original/raw data, use `danger-full-access`,
or make large paid API/cloud calls.

## Current Recommendation

Keep the Mac mini on. Do not use `openai/codex-action@v1` until a separate
OpenAI API quota is intentionally enabled.
