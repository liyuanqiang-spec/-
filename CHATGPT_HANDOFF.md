# CHATGPT_HANDOFF.md

## Purpose

This file is the persistent handoff note for future ChatGPT conversations. It records how ChatGPT should supervise Codex for the user's Mac mini quant project.

## User Preference

- The user wants to mainly talk only with ChatGPT.
- ChatGPT should act as supervisor / product manager / reviewer.
- Codex should act as the execution agent on the Mac mini.
- Avoid asking the user to copy-paste between ChatGPT and Codex unless the GitHub/Codex bridge fails.
- Keep responses concise and action-oriented.

## Active Repository

- GitHub repository: `liyuanqiang-spec/-`
- Default branch: `main`
- Repository visibility: public
- Do not store secrets, API keys, account passwords, brokerage credentials, private trading credentials, or sensitive personal financial data in this public repository.

## Current Communication Model

ChatGPT and Codex do not directly chat with each other in real time. The working bridge is GitHub:

1. User tells ChatGPT what to do.
2. ChatGPT reads current repo state, especially `STATUS.md`, `TASK_QUEUE.md`, `RUN_LOG.md`, `DECISION_REQUIRED.md`, and reports under `REPORTS/`.
3. ChatGPT updates `TASK_QUEUE.md`, `AGENTS.md`, `PROJECT_PLAN.md`, or other planning files as needed.
4. The Mac mini Codex worker checks the repository on a schedule and executes safe tasks.
5. Codex writes results back to `STATUS.md`, `RUN_LOG.md`, `REPORTS/`, and `DECISION_REQUIRED.md`.
6. ChatGPT reads the updated files and continues supervision.

Current recommended mode: `MAC_MINI_LOCAL_WORKER`.

Do not depend on `openai/codex-action@v1` unless the user intentionally enables
separate OpenAI API billing/quota. The user's ChatGPT membership is enough for
this local-worker loop, but it is not the same as OpenAI API quota.

For the current loop contract, also read `GPT_CODEX_SUPERVISOR_LOOP.md` and the
project skill `.codex/skills/gpt-codex-supervisor-loop/SKILL.md`.

## Confirmed Status From Previous Setup

As of the setup check on 2026-06-27:

- Repository remote was configured as `https://github.com/liyuanqiang-spec/-.git`.
- Codex initialized the project and pushed to `main`.
- Key files exist or were created: `AGENTS.md`, `TASK_QUEUE.md`, `STATUS.md`, `RUN_LOG.md`, `DECISION_REQUIRED.md`, `RISK_CONTROL.md`, `README.md`, `PROJECT_PLAN.md`, `DATA_SCHEMA.md`, `DATA/`, `REPORTS/`, `scripts/`, `logs/`.
- Worker script: `scripts/codex_worker.sh`.
- Worker start command: `scripts/start_worker.sh`.
- Worker stop command: `scripts/stop_worker.sh`.
- Worker launchd label: `com.codex.github-supervised-worker`.
- Worker runs every 300 seconds.
- Worker sandbox: `workspace-write`.
- `danger-full-access` is disabled / not used.
- Python check passed.
- Unit tests passed.
- Compile check passed.
- Mail test was accepted by `/usr/bin/mail` to `liyuanqiang@gmail.com` with subject `Codex 已启动` and body `可以了`.
- GitHub auth completed as `liyuanqiang-spec`.
- GitHub supervision state was marked active.
- Worker state showed `WORKER_RAN_SAFE_TASK` and `worker is alive`.

## Safety Policy

Allowed by default:

- Project planning.
- Code edits in the repository.
- Python dependency checks and normal dependency installation.
- Data schema design.
- Data cleaning.
- Backtesting.
- Simulation-only trading logic.
- Report generation.
- Unit tests and compile checks.
- Git commits / PR style work if safe.

Hard stop / needs user confirmation:

- Real brokerage login.
- Real order placement.
- Real order cancellation.
- Fund transfer.
- Any live trading connection.
- Deleting original/raw data.
- Reading, printing, uploading, or exposing secrets, API keys, passwords, tokens, brokerage credentials.
- `danger-full-access`.
- System-level destructive changes.
- Large paid API or cloud calls.

## Main Project

The core project is a white/silver options and futures quantitative research system, focused first on low-liquidity option spread opportunities.

Current intended development path:

1. Maintain safe simulation-only mode.
2. Improve option data schema and validation.
3. Build the silver options spread scanner.
4. Build the minimum viable backtest engine.
5. Add realistic execution assumptions: bid/ask, queue priority, first-leg passive fill, second-leg active chase, cancellation risk, partial fill, fees, slippage, margin.
6. Generate reports under `REPORTS/`.
7. Use the reports to decide which contracts deserve deeper tick/order-book data.

## Future ChatGPT Behavior

When the user asks to continue, check repository state first, especially:

- `STATUS.md`
- `TASK_QUEUE.md`
- `RUN_LOG.md`
- `DECISION_REQUIRED.md`
- Latest files in `REPORTS/`

Then either:

- give a concise progress summary, or
- update `TASK_QUEUE.md` with the next safe Codex task, or
- ask for confirmation only when a hard-stop item appears.

Do not claim direct real-time control over Codex. The accurate description is: ChatGPT operates Codex through a GitHub-mediated task/status loop.
