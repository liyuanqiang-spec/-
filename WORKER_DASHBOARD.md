# Worker Dashboard

Last dashboard update: `2026-06-29 20:11:22 +0800`

| Item | Result |
|---|---|
| Worker state | WORKING |
| Visible scaffold | WORKER_BUSY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | ACTIVE |
| Current poll interval | 600s |
| Consecutive idle checks | 6 |
| Polling reason | idle backoff after 6 checks |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | TASK-023-LOCAL-MAIL-DELIVERY-VERIFY (running) - Local worker mail delivery verification / worker started |
| First pending task | None |
| Latest completed task | TASK-022-LOCAL-MAIL-RETRY (completed) - Local worker mail retry / LOCAL_WORKER_MAIL_SENT |
| Latest failed or blocked task | None |
| Latest status | WORKER_RUNNING |
| Last worker check | 2026-06-29T20:11:22+08:00 / running / TASK-023-LOCAL-MAIL-DELIVERY-VERIFY |
| Latest report | REPORTS/first_complete_simulation_report.md |
| Latest push/commit | 57203b1 2026-06-29 Queue local mail delivery verification |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | No unresolved item |
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
