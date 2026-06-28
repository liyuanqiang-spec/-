# Worker Dashboard

Last dashboard update: `2026-06-28 23:31:17 +0800`

| Item | Result |
|---|---|
| Worker state | WORKING |
| Visible scaffold | WORKER_BUSY |
| Worker mode | ACTIVE |
| Current poll interval | 600s |
| Consecutive idle checks | 9 |
| Polling reason | idle backoff after 9 checks |
| Current task | TASK-016 (running) - Prepare repository-local model review packet |
| First pending task | None |
| Latest completed task | TASK-015 (completed) - Add adaptive polling frequency for local GitHub worker / completed; added adaptive ACTIVE/WARM/IDLE polling, visible polling state, health checks, and a local Terminal monitor window入口. |
| Latest failed or blocked task | TASK-014 (decision_required) - Show scaffold readiness in GPT visible status / blocked by risk control. |
| Latest status | WORKER_RUNNING |
| Last worker check | 2026-06-28T23:31:17+08:00 / running / TASK-016 |
| Latest report | REPORTS/first_complete_simulation_report.md |
| Latest push/commit | b7fa2b6 2026-06-28 Append TASK-016 safe model review packet bridge |
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
