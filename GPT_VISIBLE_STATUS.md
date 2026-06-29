# GPT Visible Status

- Generated at: `2026-06-29T20:14:53+08:00`
- Status: `IDLE`
- Visible scaffold: `SCAFFOLD_READY`
- Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`
- Local review input: `GPT_LOCAL_REVIEW_INPUT.md`
- Worker mode: `IDLE`
- Current poll interval: `600s`
- Consecutive idle checks: `6`
- Polling reason: idle backoff after 6 checks
- Night quiet window: `22:00-08:00`, active `False`, warm `600s`, idle `1800s`
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: none
- Latest completed task: TASK-023-LOCAL-MAIL-DELIVERY-VERIFY (completed) - Local worker mail delivery verification | codex exec completed
- Decision required: none
- Latest status marker: `WORKER_COMPLETED`
- Last worker check: 2026-06-29T20:14:53+08:00 / completed / TASK-023-LOCAL-MAIL-DELIVERY-VERIFY
- Latest commit: 552580c 2026-06-29 Worker started TASK-023-LOCAL-MAIL-DELIVERY-VERIFY
- Worker poll interval: active 30s, warm 60s, idle 600s
- Next action: ChatGPT 可以向 TASK_QUEUE.md 写入下一项安全任务。

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.
