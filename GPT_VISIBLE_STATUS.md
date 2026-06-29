# GPT Visible Status

- Generated at: `2026-06-29T19:36:27+08:00`
- Status: `BLOCKED`
- Visible scaffold: `SCAFFOLD_READY`
- Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`
- Local review input: `GPT_LOCAL_REVIEW_INPUT.md`
- Worker mode: `ACTIVE`
- Current poll interval: `30s`
- Consecutive idle checks: `0`
- Polling reason: new pending safe task detected
- Night quiet window: `22:00-08:00`, active `False`, warm `600s`, idle `1800s`
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: none
- Latest completed task: TASK-022-LOCAL-MAIL-RETRY (completed) - Local worker mail retry | codex exec completed
- Decision required: yes - Task TASK-020-GPT-INTERACTIVE-REPLY contains a blocked trading/fund/secret/deletion/danger risk
- Latest status marker: `WORKER_COMPLETED`
- Last worker check: 2026-06-29T19:36:27+08:00 / completed / TASK-022-LOCAL-MAIL-RETRY
- Latest commit: 97b90cf 2026-06-29 Worker started TASK-022-LOCAL-MAIL-RETRY
- Worker poll interval: active 30s, warm 60s, idle 600s
- Next action: 人工处理 DECISION_REQUIRED.md 中未解决事项，然后重新刷新状态。

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.
