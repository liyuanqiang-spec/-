# Worker Dashboard

Last dashboard update: `2026-07-02 08:54:05 +0800`

| Item | Result |
|---|---|
| Worker state | BLOCKED |
| Visible scaffold | SCAFFOLD_READY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | WARM |
| Current poll interval | 60s |
| Consecutive idle checks | 3 |
| Polling reason | idle check 3/5 |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | None |
| First pending task | None |
| Latest completed task | TASK-028-GPT-MARKER-ROUNDTRIP-TEST (completed) - GPT marker roundtrip smoke test / GPT_CODEX_MARKER_ROUNDTRIP_OK; GPT handshake completed by local worker |
| Latest failed or blocked task | TASK-029-GPT-REPLY-ROUNDTRIP (decision_required) - GPT reply roundtrip to Codex / blocked by risk control |
| Latest status | DECISION_REQUIRED |
| Last worker check | 2026-07-02T08:54:05+08:00 / blocked / TASK-029-GPT-REPLY-ROUNDTRIP |
| Latest report | REPORTS/first_complete_simulation_report.md |
| Latest push/commit | 5222f6b 2026-07-02 Append GPT reply roundtrip task |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | Yes - Task TASK-029-GPT-REPLY-ROUNDTRIP contains a blocked trading/fund/secret/deletion/danger risk |
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
