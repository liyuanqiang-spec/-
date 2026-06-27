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
```

Worker logs:

```text
logs/worker.log
```

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
