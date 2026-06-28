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
- Request: Complete the repository status layer using the files already created by ChatGPT. Refresh GPT_VISIBLE_STATUS.md, GPT_REVIEW.md, .gpt_state.json, and WORKER_DASHBOARD.md. Keep work limited to repository status, planning, tests, and simulation-only reporting.
- Expected output: refreshed visible status, review log note, state file, dashboard, tests.
- Safety: repository_status_only
- Created: 2026-06-28
- Last update: completed by Codex 2026-06-28 12:38:15 +0800
- Result: TASK-008 completed; GPT visible status layer, worker dashboard refresh, structured state file, health check, and worker reporting hooks stabilized.

### TASK-009
- Status: completed
- Type: quant_system_enhancement
- Title: Build quant system enhancement baseline
- Request: Read QUANT_SYSTEM_TARGETS.md and RELIABILITY_RUNBOOK.md. Audit the current repository against the quant-system target. Use existing backtest or sample data in the repository where available. If a needed dataset is absent, create a small documented fixture only for schema and pipeline validation, and clearly mark it as non-performance data. Implement the safest missing repository-local pieces that can be completed with data replay and simulation. Focus on data schema, option-chain scanner, time-value radar, combination generator, scoring engine, state-machine simulator, second-leg protection simulator, replay report, and dashboard/report refresh. Preserve the visible status flow. Write REPORTS/quant_system_gap_report.md and REPORTS/backtest_baseline_report.md with current coverage, data coverage, tests, and next three safe Codex tasks.
- Expected output: quant system gap report, backtest baseline report, implemented safe missing pieces where practical, refreshed dashboard, refreshed GPT visible status, passing health checks and tests or exact failure reasons.
- Safety: repository_only_simulation
- Created: 2026-06-28
- Last update: completed by Codex 2026-06-28 15:02:53 +0800
- Result: completed; generated quant gap report, backtest baseline report, replay CSV, time-value radar, scoring/state-machine replay baseline, and tests.

### TASK-010
- Status: completed
- Type: quant_replay_data
- Title: Add multi-snapshot option quote replay fixture and loader
- Request: Continue from TASK-009. Keep the repository in `PHASE_1_SIMULATION_ONLY`. Do not connect to any broker, trading account, live market feed, paid API, credential, or external execution system. Use only repository-local fixture/sample data. Add a documented multi-snapshot silver option quote replay fixture with timestamps, bid/ask, bid/ask size or depth, quote freshness/staleness fields, and enough rows to replay at least two vertical-spread candidates across multiple time steps. Implement or improve the repository-local replay loader so the state-machine simulator can consume ordered snapshots, measure first-leg timeout, quote staleness, passive fill probability, second-leg adverse move, incomplete-leg outcomes, and deterministic repricing/timeout behavior. Integrate the replay into the existing baseline pipeline and reports without removing TASK-009 outputs.
- Expected output: new or updated local fixture under DATA, replay loader/module changes, deterministic unit tests for ordered replay, stale quote handling, timeout/incomplete-leg handling, and second-leg protection; refreshed `REPORTS/backtest_baseline_report.md`, `REPORTS/quant_system_gap_report.md`, `WORKER_DASHBOARD.md`, and `GPT_VISIBLE_STATUS.md`; preserve or update `REPORTS/quant_baseline_replay.csv` as appropriate; include exact failure reasons if any check fails.
- Required checks: run `python3 scripts/refresh_visible_status.py`, `bash scripts/check_worker_health.sh`, `python3 -m compileall -q src tests scripts`, `python3 -m unittest discover -s tests`, and `bash -n scripts/codex_worker.sh`.
- Safety: repository_only_simulation
- Created: 2026-06-28
- Last update: synced by Codex 2026-06-28 20:26:43 +0800
- Result: completed; added repository-local multi-snapshot quote replay fixture, replay loader, deterministic stale quote/timeout/incomplete-leg tests, and refreshed baseline replay reports. Git result sync was rebased over TASK-011 and recorded in the queue.

### TASK-011
- Status: decision_required
- Type: local_tqsdk_tick_validation
- Title: Run local TqSdk account and historical tick data smoke test
- Request: Continue only after TASK-010 is completed or safely skipped. Run this on the local Mac mini worker environment, not in ChatGPT cloud. The user says a TqSdk account has already been provided locally and historical data has already been downloaded. Keep the repository in `PHASE_1_SIMULATION_ONLY`. Do not connect to any real broker trading account. Do not instantiate real trading gateways/accounts. Do not place, cancel, modify, or simulate sending real orders through any broker. Do not move funds. Do not commit credentials, phone numbers, verification codes, tokens, passwords, account IDs, or raw large data files.

  Safely test TqSdk and existing local historical data for the silver option replay system:
  1. Detect whether `tqsdk` is installed in the project Python environment. If absent, install only if it is safe and local to the project environment; otherwise write the exact install command needed.
  2. Detect credential availability only from local environment variables or local non-committed config, such as `TQ_USER` and `TQ_PASS`. Never print secret values; report only present/absent.
  3. Discover already downloaded historical data under repository-local `DATA/` and reasonable local project data folders. Do not scan the whole disk. Do not commit large raw files.
  4. Build `scripts/test_tqsdk_tick_access.py` that can run in two modes:
     - local-file mode: parse existing downloaded TqSdk/historical tick CSV files and map them into the repository replay schema.
     - account-data mode: when credentials are available, run a minimal market-data-only smoke test to query silver futures/options symbols and a very small tick sample. Use market data/read-only calls only. Close the API cleanly.
  5. Confirm whether silver option tick fields needed by the strategy are available: timestamp/datetime, symbol, bid_price1, bid_volume1, ask_price1, ask_volume1, last_price, volume, open_interest, trading_date if present, and source.
  6. Create an adapter/import path from TqSdk tick CSV or small tick sample into the existing multi-snapshot replay schema from TASK-010.
  7. Generate a tiny sanitized fixture from local historical data if available, clearly marked as non-performance sample, and keep any large files out of git.
  8. Run the current replay/backtest pipeline using the imported tiny TqSdk-derived fixture if possible. If not possible, explain the exact blocker: missing credentials, missing permission, missing historical files, unsupported symbol, import error, or schema mismatch.

- Expected output: `scripts/test_tqsdk_tick_access.py`, optional adapter module under `src/codex_quant/`, tiny sanitized TqSdk-derived fixture under `DATA/` if available, updated `.gitignore` if needed, `REPORTS/tqsdk_local_tick_smoke_report.md`, updated `REPORTS/quant_system_gap_report.md`, updated `REPORTS/backtest_baseline_report.md` if replay integration runs, refreshed `WORKER_DASHBOARD.md` and `GPT_VISIBLE_STATUS.md`.
- Required checks: run `python3 scripts/test_tqsdk_tick_access.py --local-only` if local files exist; run account-data mode only if credentials are available without exposing secrets; run `python3 scripts/refresh_visible_status.py`; run `bash scripts/check_worker_health.sh`; run `python3 -m compileall -q src tests scripts`; run `python3 -m unittest discover -s tests`; run `bash -n scripts/codex_worker.sh`.
- Safety: local_market_data_only_simulation_no_trading
- Created: 2026-06-28
