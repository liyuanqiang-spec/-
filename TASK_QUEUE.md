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
- Status: pending
- Type: offline_tick_file_validation
- Title: Validate local historical tick files with offline replay adapter
- Request: Continue after TASK-010. Keep work inside repository files and PHASE_1_SIMULATION_ONLY. Use only local fixture or already-present historical tick files under DATA and nearby project data folders. Do not scan the whole disk. Build an offline parser that maps available tick CSV columns into the replay snapshot schema. Required fields to check: datetime, symbol, bid_price1, bid_volume1, ask_price1, ask_volume1, last_price, volume, open_interest, trading_date, source. Create a tiny sanitized fixture only when suitable local rows exist. Run the replay or explain the exact local-file blocker such as missing file, missing column, unsupported symbol, import error, or schema mismatch. Refresh reports and visible status.
- Expected output: offline tick parser script, optional adapter module, tiny sanitized fixture when available, REPORTS/tick_file_smoke_report.md, refreshed quant reports, refreshed WORKER_DASHBOARD.md and GPT_VISIBLE_STATUS.md.
- Required checks: python3 scripts/refresh_visible_status.py; bash scripts/check_worker_health.sh; python3 -m compileall -q src tests scripts; python3 -m unittest discover -s tests; bash -n scripts/codex_worker.sh.
- Safety: offline_repository_file_validation_only
- Created: 2026-06-28
- Last update: created by ChatGPT
- Result: pending
