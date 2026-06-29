# GPT Visible Status

- Generated at: `2026-06-29T20:00:08+08:00`
- Status: `IDLE`
- Visible scaffold: `SCAFFOLD_READY`
- Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`
- Local review input: `GPT_LOCAL_REVIEW_INPUT.md`
- Worker mode: `IDLE`
- Current poll interval: `600s`
- Consecutive idle checks: `5`
- Polling reason: idle backoff after 5 checks
- Night quiet window: `22:00-08:00`, active `False`, warm `600s`, idle `1800s`
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: none
- Latest completed task: TASK-022-LOCAL-MAIL-RETRY (completed) - Local worker mail retry | codex exec completed
- Decision required: none
- Latest status marker: `DEFAULT_MAIL_RULE_CONFIGURED`
- Last worker check: 2026-06-29T19:36:27+08:00 / completed / TASK-022-LOCAL-MAIL-RETRY
- Latest commit: be0ad09 2026-06-29 Sync TASK-022 completion and clear stale decisions
- Worker poll interval: active 30s, warm 60s, idle 600s
- Next action: ChatGPT 可以向 TASK_QUEUE.md 写入下一项安全任务。

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.
