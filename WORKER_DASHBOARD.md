# Worker Dashboard

Last dashboard update: `2026-06-29 17:11:58 +0800`

| Item | Result |
|---|---|
| Worker state | BLOCKED |
| Visible scaffold | SCAFFOLD_READY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | WARM |
| Current poll interval | 600s |
| Consecutive idle checks | 7 |
| Polling reason | idle backoff after 7 checks |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | None |
| First pending task | None |
| Latest completed task | TASK-019A (completed) - Verify local supervisor loop / GPT handshake completed by local worker |
| Latest failed or blocked task | TASK-020-GPT-INTERACTIVE-REPLY (decision_required) - GPT interactive reply to Codex / blocked by risk control |
| Latest status | DECISION_REQUIRED |
| Last worker check | 2026-06-29T17:11:58+08:00 / blocked / TASK-020-GPT-INTERACTIVE-REPLY |
| Latest report | REPORTS/software_progress_audit.md |
| Latest push/commit | ec7cb73 2026-06-29 Append GPT interactive reply task |
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
