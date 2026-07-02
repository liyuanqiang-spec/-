# Worker Dashboard

Last dashboard update: `2026-07-02 15:09:35 +0800`

| Item | Result |
|---|---|
| Worker state | BLOCKED |
| Visible scaffold | SCAFFOLD_READY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | WARM |
| Current poll interval | 600s |
| Consecutive idle checks | 51 |
| Polling reason | idle backoff after 51 checks |
| Night quiet window | 22:00-08:00 active=False |
| Night poll interval | warm 600s, idle 1800s |
| Current task | None |
| First pending task | None |
| Latest completed task | TASK-031-ASK-SOFTWARE-ITERATION-STATUS (completed) - Ask Codex for software iteration progress [SOFTWARE_ITERATION_STATUS_20260702] / codex exec completed |
| Latest failed or blocked task | TASK-032-IWENCAI-SKILLHUB-VOLATILITY (decision_required) - Install and export Iwencai SkillHub volatility strategy skill |
| Latest status | DECISION_REQUIRED |
| Last worker check | 2026-07-02T15:09:35+08:00 / blocked / TASK-032-IWENCAI-SKILLHUB-VOLATILITY |
| Latest report | REPORTS/first_complete_simulation_report.md |
| Latest push/commit | ddab9bf 2026-07-02 Queue Codex task for Iwencai volatility skill export |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | Yes - Task TASK-032-IWENCAI-SKILLHUB-VOLATILITY contains a blocked trading/fund/secret/deletion/danger risk |
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
