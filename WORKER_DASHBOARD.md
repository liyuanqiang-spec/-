# Worker Dashboard

Last dashboard update: `2026-09-07 09:14:25 +0800`

| Item | Result |
|---|---|
| Worker state | WAITING_FOR_WORKER |
| Visible scaffold | SCAFFOLD_READY |
| Local review trigger | LOCAL_REVIEW_TRIGGER_DRY_RUN_READY |
| Local review input | GPT_LOCAL_REVIEW_INPUT.md |
| Worker mode | WAITING_FOR_WORKER |
| Current poll interval | 1800s |
| Consecutive idle checks | 56 |
| Polling reason | idle backoff after 56 checks; night quiet window 22:00-08:00 |
| Night quiet window | 22:00-08:00 active=True |
| Night poll interval | warm 600s, idle 1800s |
| Current task | None |
| First pending task | TASK-033-SILVER-V1-STATUS-REFRESH |
| Latest completed task | TASK-032A-IWENCAI-SKILLHUB-PACKAGE (completed) - Iwencai SkillHub package export / IWENCAI_SKILLHUB_SETUP_BLOCKED_20260702; Codex replied to GPT that SkillHub CLI was not available locally, the CLI-only setup endpoint was not reachable from this worker session, `skillhub_export/iwencai_skillhub_install_report.md` was written, and no tar.gz export was produced. |
| Latest failed or blocked task | None |
| Latest status | WORKER_COMPLETED |
| Last worker check | 2026-07-02T15:20:12+08:00 / completed / TASK-032A-IWENCAI-SKILLHUB-PACKAGE |
| Latest report | REPORTS/first_complete_simulation_report.md |
| Latest push/commit | af46c78 2026-09-07 Queue silver option V1 status refresh |
| Worker poll interval | active 30s, warm 60s, idle 600s |
| Decision required | No unresolved item |
| Safety mode | PHASE_1_SIMULATION_ONLY |
| Next action | Local worker should pull and execute TASK-033-SILVER-V1-STATUS-REFRESH. |

## Links

- [Task queue](TASK_QUEUE.md)
- [Status](STATUS.md)
- [Run log](RUN_LOG.md)
- [Decision required](DECISION_REQUIRED.md)
- [Risk control](RISK_CONTROL.md)
- [Reliability runbook](RELIABILITY_RUNBOOK.md)
- [GPT visible status](GPT_VISIBLE_STATUS.md)
