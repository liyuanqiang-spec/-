---
name: gpt-codex-supervisor-loop
description: Use when ChatGPT supervises the Mac mini Codex worker through GitHub task/status files, with local execution and GPT-visible feedback.
---

# GPT-Codex Supervisor Loop

## Goal

Let ChatGPT act as planner, supervisor, and reviewer while the Mac mini Codex
worker executes safe repository tasks.

## Source Of Truth

Read these files in order:

1. `TASK_QUEUE.md`
2. `GPT_VISIBLE_STATUS.md`
3. `WORKER_DASHBOARD.md`
4. `STATUS.md`
5. `RUN_LOG.md`
6. `GPT_REVIEW.md`
7. `GPT_LOCAL_REVIEW_INPUT.md`
8. `DECISION_REQUIRED.md`

## Workflow

1. ChatGPT writes exactly one next safe task to `TASK_QUEUE.md`.
2. The Mac mini worker pulls `main`.
3. The worker executes the first pending safe task.
4. The worker updates status and review files.
5. The worker commits and pushes results.
6. ChatGPT reads `GPT_LOCAL_REVIEW_INPUT.md` and `GPT_REVIEW.md`, then improves the next task.

## Timing

- Active task polling: about 30 seconds.
- Warm period after activity: about 60 seconds.
- Idle polling: about 600 seconds.

## Safety

Allowed:

- Planning, coding, data cleaning, scanning, backtesting, simulation, and reports.

Hard stop:

- Real trading account connection.
- Real order placement or cancellation.
- Fund or margin movement.
- Secret, token, password, or API key exposure.
- Original/raw data deletion.
- `danger-full-access`.
- Large paid API/cloud calls.

## Output Contract

Every worker cycle must leave these surfaces clear:

- Current state in `GPT_VISIBLE_STATUS.md`.
- Execution details in `RUN_LOG.md`.
- Durable summary in `STATUS.md`.
- GPT handoff in `GPT_REVIEW.md` and `GPT_LOCAL_REVIEW_INPUT.md`.
- Human-only blockers in `DECISION_REQUIRED.md`.
