# Worker Dashboard

Last dashboard update: `2026-06-29 19:36:27 +0800`

| Item | Result |
|---|---|
| Worker state | BLOCKED |
| Visible scaffold | SCAFFOLD_READY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | ACTIVE |
| Current poll interval | 30s |
| Consecutive idle checks | 0 |
| Polling reason | new pending safe task detected |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | None |
| First pending task | None |
| Latest completed task | TASK-022-LOCAL-MAIL-RETRY (completed) - Local worker mail retry / codex exec completed |
| Latest failed or blocked task | TASK-020-GPT-INTERACTIVE-REPLY (decision_required) - GPT interactive reply to local worker / blocked by local guard |
| Latest status | WORKER_COMPLETED |
| Last worker check | 2026-06-29T19:36:27+08:00 / completed / TASK-022-LOCAL-MAIL-RETRY |
| Latest report | REPORTS/software_progress_audit.md |
| Latest push/commit | 97b90cf 2026-06-29 Worker started TASK-022-LOCAL-MAIL-RETRY |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | Yes - Task TASK-020-GPT-INTERACTIVE-REPLY contains a blocked trading/fund/secret/deletion/danger risk |
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
