# Silver Options Quant Worker

查看工作状态: [WORKER_DASHBOARD.md](WORKER_DASHBOARD.md)

This repository is the GitHub-supervised workspace for a silver options/futures quantitative research system.

Current mode: `PHASE_1_SIMULATION_ONLY`

## Safety Boundary

Allowed:

- Data download
- Data cleaning
- Strategy scanning
- Backtesting
- Simulated trading
- Report generation

Blocked:

- Real trading account connection
- Real order placement
- Real order cancellation
- Fund transfer
- Original/raw-data deletion
- API key, password, token, or secret exposure
- `danger-full-access`

## GitHub Supervision Flow

1. ChatGPT updates `TASK_QUEUE.md` on GitHub.
2. The Mac mini worker pulls `main`.
3. The worker reads the first pending safe task.
4. The worker calls `codex exec --sandbox workspace-write`.
5. Codex updates files, tests, reports, `STATUS.md`, and `RUN_LOG.md`.
6. The worker commits and pushes the result to GitHub.

## Worker Commands

```bash
scripts/start_worker.sh
scripts/stop_worker.sh
scripts/codex_worker.sh --dry-run
scripts/check_worker_health.sh
```

Manual on-demand health check:

```bash
scripts/check_worker_health.sh
```

Worker logs:

```text
logs/worker.log
```

## First Complete Simulation Command

Run the TASK-007 simulation-only silver option liquidity radar:

```bash
python3 -m src.codex_quant.run_pipeline --first-complete-simulation
```

Outputs:

- `REPORTS/first_complete_simulation_report.md`: complete Markdown report.
- `REPORTS/first_complete_simulation_summary.json`: dashboard metrics for contracts scanned, candidates, rejected candidates, average simulated edge, worst simulated slippage, and risk flags.
- `REPORTS/latest_report.md`: compatibility report for the earlier minimal pipeline.

This command uses only local sample data from `data/contracts/sample_options.csv`. It does not connect to real trading accounts, place or cancel real orders, transfer funds, read credentials, or use `danger-full-access`.

## Main Files

- `AGENTS.md`: unattended agent rules
- `TASK_QUEUE.md`: GitHub task queue
- `STATUS.md`: current state
- `RUN_LOG.md`: execution log
- `DECISION_REQUIRED.md`: human confirmation queue
- `RISK_CONTROL.md`: safety and kill switches
- `DATA_SCHEMA.md`: data field standard
- `DATA/`: market data workspace
- `REPORTS/`: generated reports
- `scripts/`: worker controls
