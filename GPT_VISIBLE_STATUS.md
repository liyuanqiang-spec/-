# GPT Visible Status

- Generated at: `2026-06-29T11:36:10+08:00`
- Status: `BLOCKED`
- Visible scaffold: `SCAFFOLD_READY`
- Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`
- Local review input: `GPT_LOCAL_REVIEW_INPUT.md`
- Worker mode: `WARM`
- Current poll interval: `60s`
- Consecutive idle checks: `0`
- Polling reason: not yet recorded
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: none
- Latest completed task: TASK-018 (completed) - Make local review input visible in GitHub | codex exec completed
- Decision required: yes - Task TASK-019 contains a blocked trading/fund/secret/deletion/danger risk
- Latest status marker: `DECISION_REQUIRED`
- Last worker check: 2026-06-29T11:36:10+08:00 / blocked / TASK-019
- Latest commit: 1f6d09c 2026-06-29 Enable local GPT Codex supervisor loop
- Worker poll interval: active 30s, warm 60s, idle 600s
- Next action: 人工处理 DECISION_REQUIRED.md 中未解决事项，然后重新刷新状态。

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.
