# GPT Visible Status

- Generated at: `2026-06-28T21:21:24+08:00`
- Status: `BLOCKED`
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: none
- Latest completed task: TASK-012 (completed) - Reduce idle worker calls and writes | codex exec completed.
- Decision required: yes - Task TASK-013 contains a blocked trading/fund/secret/deletion/danger risk
- Latest status marker: `DECISION_REQUIRED`
- Last worker check: 2026-06-28T21:21:24+08:00 / blocked / TASK-013
- Latest commit: 71ab834 2026-06-28 Add GPT auto review workflow task
- Worker poll interval: idle 600s, active 60s
- Next action: 人工处理 DECISION_REQUIRED.md 中未解决事项，然后重新刷新状态。

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.
