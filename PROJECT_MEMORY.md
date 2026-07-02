# PROJECT_MEMORY.md

## Project

Silver option liquidity-radar project.

## Core strategy

Use passive posting on low-liquidity option legs and active hedging on the liquid leg. The goal is to improve combo net execution price. Current phase is simulation, backtest, reports, and risk checks only.

## Current architecture

- GitHub is the task ledger.
- TASK_QUEUE.md is the instruction queue from GPT to the local worker.
- The local worker reads safe pending tasks and writes STATUS.md, RUN_LOG.md, reports, and code.
- GPT orchestrator reviews worker output and appends the next safe task.
- User wants both worker feedback and GPT review feedback visible in repository files and available for ChatGPT summaries.

## GPT-Codex GitHub handoff memory

Status: established and reusable.

- Shared repository: `liyuanqiang-spec/-`
- Default branch: `main`
- Git remote: `https://github.com/liyuanqiang-spec/-.git`
- Primary queue: `TASK_QUEUE.md`
- Detailed task directory: `TASK_QUEUE/`
- Main status surfaces: `STATUS.md`, `RUN_LOG.md`, `GPT_VISIBLE_STATUS.md`, `GPT_CODEX_CONVERSATION.md`
- Human decision queue: `DECISION_REQUIRED.md`
- Risk boundary: `RISK_CONTROL.md`
- Reusable skill: `.codex/skills/gpt-codex-github-handoff/SKILL.md`

Operational rule: when the owner asks ChatGPT to instruct Codex, do not ask for the repository again unless GitHub access fails. Use the GitHub connector, append a safe pending task to `TASK_QUEUE.md`, create a detailed task file under `TASK_QUEUE/` when needed, and later read Codex's pushed result files.

Known successful route markers:

- `GPT_CODEX_INTERACTION_TEST_OK`
- `GPT_CODEX_MARKER_ROUNDTRIP_OK`
- `GPT_REPLY_RECEIVED_20260702_OK`
- `GPT_CODEX_RETEST_20260702_OK`

## Software roles

- InfiniTrader: candidate execution endpoint, custom spread, priority-leg mode, PythonGo protection layer.
- Kuaqi 3: T-shaped option quote, dynamic export, option/futures and expiry handling support.
- WingChun/Huidian: option matrix, Greeks, IV, PnL, and risk analysis.

## Must build

- Time-value radar.
- Low-liquidity spread scan.
- Tradable spread judgment.
- Anti-chasing state machine.
- Second-leg net-price protection after first-leg fill.
- Logs, replay, and reports.

## Core KPI

- Average net-price improvement.
- Complete close success rate.
- Broken-leg rate.
- Hedge time for second leg.
- Worst adverse move.
- Cancel/fill ratio.

## Safety boundaries

- Simulation mode only.
- No live brokerage link.
- No live order operation.
- No money movement.
- No credentials in repository.
- No destructive data deletion.

## Immediate priority

Continue the existing src/codex_quant framework and produce the first complete simulation version.
