# TASK_QUEUE.md

Purpose: ChatGPT/Codex uses this file as the safe handoff queue. The worker only executes `pending` or `queued` tasks whose type is explicitly safe.

Allowed task types:

- `pipeline`
- `report`
- `test`
- `status_check`

Blocked without confirmation: real trading, real orders, cancels, fund transfer, broker permission change, raw-data deletion, secret exposure, danger-full-access, system-level changes, and large paid calls.

## Queue

### TQ-0001
- Status: completed
- Type: pipeline
- Request: Run the sample silver options/futures research pipeline and regenerate the latest report.
- Created: 2026-06-27
- Last update: 2026-06-27T12:56:30+08:00
- Result: pipeline completed: contracts=7, candidates=4, report=/Users/zhoujiali/Documents/学习codex/REPORTS/latest_report.md

### TQ-0002
- Status: completed
- Type: test
- Request: Run the local test suite after the unattended worker scaffold is installed.
- Created: 2026-06-27
- Last update: 2026-06-27T12:56:31+08:00
- Result: tests passed: ---------------------------------------------------------------------- Ran 3 tests in 0.000s  OK

### TQ-0003
- Status: completed
- Type: status_check
- Request: Verify the launchd scheduled worker can process a new queue item.
- Created: 2026-06-27
- Last update: 2026-06-27T13:04:16+08:00
- Result: status files readable; worker is alive
