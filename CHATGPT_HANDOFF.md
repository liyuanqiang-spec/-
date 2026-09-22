# CHATGPT_HANDOFF.md

## 2026-09-22 live verification overrides historical claims

The legacy GitHub queue worker is NOT currently installed or running on the local Mac mini. Its last repository heartbeat is 2026-07-02. The local project instructions designate the old TASK_QUEUE loop as legacy. Writing a queue file alone does not launch local Codex.

TASK-034 has been explicitly taken over by the owner-authorized current local Codex task. Do not describe historical handshake success as current connectivity. Require a fresh task-specific pickup marker and an execution result. Pending without pickup means not started.


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

ChatGPT and Codex do not directly chat with each other in real time. The working bridge is GitHub, with a local read-only conversation window for visibility:

1. User tells ChatGPT what to do.
2. ChatGPT reads current repo state, especially `STATUS.md`, `TASK_QUEUE.md`, `RUN_LOG.md`, `DECISION_REQUIRED.md`, and reports under `REPORTS/`.
3. ChatGPT updates `TASK_QUEUE.md`, `AGENTS.md`, `PROJECT_PLAN.md`, or other planning files as needed.
4. The Mac mini Codex worker checks the repository on a schedule and executes safe tasks.
5. Codex writes results back to `STATUS.md`, `RUN_LOG.md`, `REPORTS/`, and `DECISION_REQUIRED.md`.
6. ChatGPT reads the updated files and continues supervision.

Current recommended mode: `MAC_MINI_LOCAL_WORKER`.

Current route marker: `LOCAL_WORKER_PRIMARY_ROUTE_READY`.

The Mac mini worker is the active execution route. Hosted execution remains
parked for later; future GPT tasks should use clean repository-status wording
and avoid restating blocked setup details inside task requests.

Visible local surfaces:

- `GPT_CODEX_CONVERSATION.md` shows the GPT -> Codex task timeline and Codex -> GPT results.
- Desktop command: `/Users/zhoujiali/Library/Mobile Documents/com~apple~CloudDocs/Desktop/查看GPT和Codex对话.command`.
- `WORKER_DASHBOARD.md` and `GPT_VISIBLE_STATUS.md` show the worker state, polling mode, and night quiet window.

Current polling policy:

- Daytime normal path: `ACTIVE=30s`, `WARM=60s`, `IDLE=600s`.
- Night quiet window: `22:00-08:00`; no-pending `WARM=600s`, no-pending `IDLE=1800s`.
- Health guard label: `com.codex.github-worker-health-guard`; it checks locally every `900s` and restarts the worker if needed. This does not spend model tokens.

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
- Worker uses adaptive polling: active 30 seconds, warm 60 seconds, idle 600 seconds, with a 22:00-08:00 night quiet window.
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

### Current supervision (2026-09-22)
The native Codex heartbeat `GitHub 本机任务接收与执行` is active every 10 minutes in the local takeover task. Following the owner's explicit 2026-09-22 request, it now claims and executes new owner-authored, authorized, safe local tasks submitted to TASK_QUEUE.md, then writes real pickup and completion/failure receipts. It does not revive the legacy shell worker or execute old TASK-033. It reviews source and scope, prevents duplicate execution, and stops at actual safety/authorization boundaries. Unchanged polling is silent. A queued task is not running until its fresh pickup receipt exists. Scheduled execution was verified by the actual native heartbeat on 2026-09-22: TASK-035 pickup, local macOS execution, and GitHub receipt writeback succeeded. See REPORTS/native_dispatch_smoke_20260922.md. Historical claims above do not revive the retired shell worker.
