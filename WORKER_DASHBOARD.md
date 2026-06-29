# Worker Dashboard

Last dashboard update: `2026-06-29 21:11:10 +0800`

| Item | Result |
|---|---|
| Worker state | BLOCKED |
| Visible scaffold | SCAFFOLD_READY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | WARM |
| Current poll interval | 600s |
| Consecutive idle checks | 8 |
| Polling reason | idle backoff after 8 checks |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | None |
| First pending task | None |
| Latest completed task | TASK-025-DIRECT-QQ-MAIL-TEST (completed) - Direct QQ mail test / CODEX_QQ_MAIL_ACCEPTED_UNVERIFIED; subject marker `CODEX-QQ-DIRECT-TEST-20260629-2045`; local mail command accepted the direct QQ test attempt, but final mailbox delivery was not independently verified. |
| Latest failed or blocked task | TASK-026-LOCAL-WORKER-PRIMARY-ROUTE (decision_required) - Adopt local worker as the primary route and park cloud API path |
| Latest status | DECISION_REQUIRED |
| Last worker check | 2026-06-29T21:11:10+08:00 / blocked / TASK-026-LOCAL-WORKER-PRIMARY-ROUTE |
| Latest report | REPORTS/first_complete_simulation_report.md |
| Latest push/commit | ce4e256 2026-06-29 Queue local worker primary route task |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | Yes - Task TASK-026-LOCAL-WORKER-PRIMARY-ROUTE contains a blocked trading/fund/secret/deletion/danger risk |
| Safety mode | PHASE_1_SIMULATION_ONLY |
| Next action | 人工处理 DECISION_REQUIRED.md 中未解决事项，然后重新刷新状态。 |

## Links

- [Task queue](TASK_QUEUE.md)
- [Status](STATUS.md)
- [Run log](RUN_LOG.md)
- [Decision required](DECISION_REQUIRED.md)
- [Risk control](RISK_CONTROL.md)
- [Reliability runbook](RELIABILITY_RUNBOOK.md)
- [GPT visible status](GPT_VISIBLE_STATUS.md)
