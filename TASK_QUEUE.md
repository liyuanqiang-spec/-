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
- Result: codex exec completed.

### TASK-007
- Status: completed
- Type: simulation_development
- Title: Build first complete simulation version for silver option liquidity radar
- Result: codex exec completed.

### TASK-008
- Status: completed
- Type: repo_status_setup
- Title: Finish GPT visible status layer
- Result: TASK-008 completed; visible status layer and worker reporting hooks stabilized.

### TASK-009
- Status: completed
- Type: quant_system_enhancement
- Title: Build quant system enhancement baseline
- Result: completed; generated quant gap report, backtest baseline report, replay CSV, time-value radar, scoring/state-machine replay baseline, and tests.

### TASK-010
- Status: completed
- Type: quant_replay_data
- Title: Add multi-snapshot option quote replay fixture and loader
- Result: completed; added repository-local multi-snapshot quote replay fixture, replay loader, deterministic stale quote/timeout/incomplete-leg tests, and refreshed baseline replay reports. Git result sync was rebased and recorded in the queue.

### TASK-011
- Status: superseded
- Type: local_tqsdk_tick_validation
- Title: Original local TqSdk smoke test wording
- Result: superseded by TASK-011A because the worker risk scanner stopped on overly broad wording.

### TASK-011A
- Status: completed
- Type: offline_tick_file_validation
- Title: Validate local historical tick files with offline replay adapter
- Result: completed; added offline tick adapter, validation script, sanitized non-performance tick fixture, tick smoke report, refreshed quant reports, and passed 21 tests.

### TASK-012
- Status: pending
- Type: worker_cost_control
- Title: Reduce idle worker calls and writes
- Request: Reduce background worker activity now that the queue is idle. Set idle polling to 600 seconds or slower, active-task polling to 60 seconds or slower, and make idle rounds read-only. When there is no pending task, do not call any model, do not run Codex, do not refresh status files, do not commit, and do not push. Keep a manual health-check command for on-demand checks. Update visible status to show the new intervals and the last worker check. Keep all work inside repository files and PHASE_1_SIMULATION_ONLY.
- Expected output: updated worker config or scripts, refreshed WORKER_DASHBOARD.md, refreshed GPT_VISIBLE_STATUS.md, STATUS.md and RUN_LOG.md note showing old interval and new interval, and passing shell/Python checks.
- Safety: repository_status_only
- Created: 2026-06-28
- Result: pending
