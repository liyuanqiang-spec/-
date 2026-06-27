# TASK_QUEUE.md

This queue is the GitHub handoff channel from ChatGPT to the local worker.

Worker rule: execute the first task whose Status is `pending` and whose Safety is safe. Do not repeat completed tasks.

## Tasks

### TASK-000-GPT-HANDSHAKE
- Status: completed
- Type: status_check
- Title: GPT to local worker handshake
- Result: GPT_HANDSHAKE_OK recorded.

### TASK-001
- Status: completed
- Type: development
- Title: MVP scaffold initialization
- Result: completed by worker.

### TASK-002
- Status: completed
- Type: data_schema
- Title: Data schema standardization
- Result: completed by worker.

### TASK-003
- Status: completed
- Type: research
- Title: Low-liquidity contract scan
- Result: completed by worker.

### TASK-004
- Status: superseded
- Type: worker_stability
- Title: Original worker stability task
- Result: superseded by TASK-004A.

### TASK-004A
- Status: completed
- Type: worker_stability_status_only
- Title: Stabilize local worker status loop
- Result: completed by worker.

### TASK-005
- Status: completed
- Type: dashboard
- Title: Create worker dashboard
- Result: completed by worker.

### TASK-006
- Status: completed
- Type: worker_stability_status_only
- Title: Change idle poll interval to 10 minutes
- Request: Update the local worker idle polling interval from 60 seconds to 600 seconds. If the config has separate idle and active intervals, set idle_poll_interval_seconds=600 and active_poll_interval_seconds=60. During idle polls, only check the repository and task queue. If there is no new pending safe task, do not call any model, do not commit, do not push, and do not write noisy logs. If a GPT orchestrator workflow exists, make sure its scheduled frequency is not faster than once every 10 minutes. Estimate from RUN_LOG.md or logs/worker.log how many polls, tasks, executions, pushes, Codex calls, and OpenAI calls occurred in the last hour; mark unclear numbers as estimates.
- Expected output: Updated worker config or equivalent startup configuration; STATUS.md section TASK-006 with current interval and last-hour estimates; RUN_LOG.md entries POLL_INTERVAL_10MIN_UPDATE_STARTED and POLL_INTERVAL_10MIN_UPDATE_DONE; dashboard updated if present.
- Safety: status_only_repo_maintenance
- Created: 2026-06-27
- Last update: updated by worker
- Result: codex exec completed
