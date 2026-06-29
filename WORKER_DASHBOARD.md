# Worker Dashboard

Last dashboard update: `2026-06-29 19:15:04 +0800`

| Item | Result |
|---|---|
| Worker state | WORKING |
| Visible scaffold | WORKER_BUSY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | ACTIVE |
| Current poll interval | 60s |
| Consecutive idle checks | 0 |
| Polling reason | unresolved blocker detected |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | TASK-021-LOCAL-MAIL-SMOKE (running) - Local worker visible smoke check / worker started |
| First pending task | None |
| Latest completed task | TASK-019A (completed) - Verify local supervisor loop / GPT handshake completed by local worker |
| Latest failed or blocked task | TASK-020-GPT-INTERACTIVE-REPLY (decision_required) - GPT interactive reply to local worker / blocked by local guard |
| Latest status | WORKER_RUNNING |
| Last worker check | 2026-06-29T19:15:04+08:00 / running / TASK-021-LOCAL-MAIL-SMOKE |
| Latest report | REPORTS/software_progress_audit.md |
| Latest push/commit | d88bd2f 2026-06-29 Queue local worker mail smoke test |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | Yes - Task TASK-020-GPT-INTERACTIVE-REPLY contains a blocked trading/fund/secret/deletion/danger risk |
| Safety mode | PHASE_1_SIMULATION_ONLY |
| Next action | 等待当前任务完成；worker 会在完成、失败或阻塞后推送状态。 |

## Links

- [Task queue](TASK_QUEUE.md)
- [Status](STATUS.md)
- [Run log](RUN_LOG.md)
- [Decision required](DECISION_REQUIRED.md)
- [Risk control](RISK_CONTROL.md)
- [Reliability runbook](RELIABILITY_RUNBOOK.md)
- [GPT visible status](GPT_VISIBLE_STATUS.md)
