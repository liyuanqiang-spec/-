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
- Status: pending
- Type: simulation_development
- Title: Build first complete simulation version for silver option liquidity radar
- Request: Continue from the existing `src/codex_quant` framework. Do not restart from zero. Build the first complete simulation-only version that can run on sample data on Sunday without market connection. Required outputs: 1) a runnable command that scans sample silver option contracts, generates vertical spread candidates, estimates passive-first-leg fill opportunity, simulates second-leg hedging, applies risk checks, and writes a Markdown report; 2) a simple dashboard/report entry showing contracts scanned, candidates, rejected candidates, average simulated edge, worst simulated slippage, and risk flags; 3) update tests so the pipeline, low-liquidity scanner, spread calculator, backtester, and risk checker all run; 4) update README with the exact command to run the first complete simulation version. Keep all work in PHASE_1_SIMULATION_ONLY. Use sample/local data only. No broker connection. No live order logic. No credentials.
- Expected output: updated Python modules under `src/codex_quant/`, updated tests, `REPORTS/first_complete_simulation_report.md`, updated `STATUS.md`, updated `RUN_LOG.md`, updated `WORKER_DASHBOARD.md` if present. Verification must include compileall and unit tests.
- Safety: simulation_only
- Created: 2026-06-28
- Last update: created by ChatGPT
- Result: pending
