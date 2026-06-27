# Codex Quant Workflow

This project is a safe, minimal Codex workspace for options and futures quant research.

## Current Scope

Allowed:

- Data download
- Data cleaning
- Option contract scanning
- Spread calculation
- Simple backtesting
- Simulated trading preparation
- Report generation

Blocked by default:

- Real order placement
- Real broker execution
- Fund transfer
- Destructive deletion of important data
- Publishing sensitive trading data

## Quick Start

```bash
python3 -m src.codex_quant.run_pipeline
```

Generated report:

```text
REPORTS/latest_report.md
```

On case-folding filesystems Git may display these as `data/` and `reports/`; the code prefers `DATA/` and `REPORTS/` locally and falls back to lowercase if needed.

Run the safe worker once:

```bash
scripts/run_worker_once.sh
```

Start/stop the background worker:

```bash
scripts/start_worker.sh
scripts/worker_status.sh
scripts/stop_worker.sh
```

The background worker is a user-level launchd scheduled job. It wakes every 300 seconds, reads `TASK_QUEUE.md`, processes safe tasks, writes `RUN_LOG.md`, then exits.

## Main Files

- `AGENTS.md`: agent rules
- `PROJECT_PLAN.md`: project plan
- `TASKS.md`: task list
- `TASK_QUEUE.md`: unattended worker queue
- `STATUS.md`: current status
- `RUN_LOG.md`: worker execution log
- `DECISION_REQUIRED.md`: human-confirmation queue
- `RISK_CONTROL.md`: trading safety controls
- `.codex/skills/`: project-specific skills
- `src/codex_quant/`: minimal runnable quant scaffold
- `scripts/`: safe worker controls
