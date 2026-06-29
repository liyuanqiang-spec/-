# GPT Visible Status

- Generated at: `2026-06-29T21:11:10+08:00`
- Status: `BLOCKED`
- Visible scaffold: `SCAFFOLD_READY`
- Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`
- Local review input: `GPT_LOCAL_REVIEW_INPUT.md`
- Worker mode: `WARM`
- Current poll interval: `600s`
- Consecutive idle checks: `8`
- Polling reason: idle backoff after 8 checks
- Night quiet window: `22:00-08:00`, active `False`, warm `600s`, idle `1800s`
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: none
- Latest completed task: TASK-025-DIRECT-QQ-MAIL-TEST (completed) - Direct QQ mail test | CODEX_QQ_MAIL_ACCEPTED_UNVERIFIED; subject marker `CODEX-QQ-DIRECT-TEST-20260629-2045`; local mail command accepted the direct QQ test attempt, but final mailbox delivery was not independently verified.
- Decision required: yes - Task TASK-026-LOCAL-WORKER-PRIMARY-ROUTE contains a blocked trading/fund/secret/deletion/danger risk
- Latest status marker: `DECISION_REQUIRED`
- Last worker check: 2026-06-29T21:11:10+08:00 / blocked / TASK-026-LOCAL-WORKER-PRIMARY-ROUTE
- Latest commit: ce4e256 2026-06-29 Queue local worker primary route task
- Worker poll interval: active 30s, warm 60s, idle 600s
- Next action: 人工处理 DECISION_REQUIRED.md 中未解决事项，然后重新刷新状态。

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.
