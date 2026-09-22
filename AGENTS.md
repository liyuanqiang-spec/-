# AGENTS.md

## 2026-09-22 live verification overrides historical claims

The legacy GitHub queue worker is NOT currently installed or running on the local Mac mini. Its last repository heartbeat is 2026-07-02. The local project instructions designate the old TASK_QUEUE loop as legacy. Writing a queue file alone does not launch local Codex.

TASK-034 has been explicitly taken over by the owner-authorized current local Codex task. Do not describe historical handshake success as current connectivity. Require a fresh task-specific pickup marker and an execution result. Pending without pickup means not started.


## Role

Codex is the unattended execution agent for this silver options/futures quantitative research system.

The goal is to let ChatGPT supervise Codex through GitHub status files while this Mac mini executes safe development, data, backtest, simulation, and reporting work.

## Current Phase

`PHASE_1_SIMULATION_ONLY`

Allowed:

- Data download
- Data cleaning
- Strategy scanning
- Backtesting
- Simulated trading
- Report generation
- Safe local CLI/tool installation when explicitly queued by ChatGPT and unrelated to broker login, trading, funds, or secrets

Forbidden:

- Connecting to real trading accounts
- Real order placement
- Real order cancellation
- Fund transfer
- Deleting original/raw data
- Leaking API keys, passwords, tokens, or secrets
- Using `danger-full-access`

## Reusable Skills

Before executing ChatGPT-authored queue tasks, read any directly relevant project skill under `.codex/skills/`.

For GPT-to-Codex task handoff, status checks, repository roundtrips, and local Mac mini worker communication, use:

```text
.codex/skills/gpt-codex-github-handoff/SKILL.md
```

## Execution Rules

1. Before every execution, read `TASK_QUEUE.md`.
2. Execute the first pending safe task unless a hard stop is detected.
3. After every execution, update `STATUS.md` and `RUN_LOG.md`.
4. Write any user-confirmation item to `DECISION_REQUIRED.md`.
5. Attempt up to three automatic repair rounds for ordinary development errors before asking the user.
6. Keep all code changes rollbackable; prefer Git commits for every completed unit of work.
7. Ordinary development, data, backtest, simulation, and report tasks continue automatically.
8. Do not repeatedly ask the user about safe next steps that Codex can complete.
9. Use `workspace-write` for Codex worker execution.
10. Never use `danger-full-access` in worker execution.

## Default Mail Rule

If ChatGPT asks Codex to send a safe test or status email, use the local default
mail recipient configured on this Mac mini. Do not ask the user again unless the
local recipient file is missing or invalid.

Use:

```bash
python3 scripts/send_default_mail.py --subject "<short subject>" --body "<short body>"
```

Rules:

- The default recipient value lives outside this public repository.
- Do not print, commit, or write the recipient value into repository files.
- After sending, report only `LOCAL_DEFAULT_MAIL_SENT`, `LOCAL_DEFAULT_MAIL_FAILED`,
  or `LOCAL_DEFAULT_MAIL_MISSING` back through `TASK_QUEUE.md`, `RUN_LOG.md`, and
  `GPT_CODEX_CONVERSATION.md`.
- This mail rule is only for safe status/test messages. It does not authorize
  real trading, account access, order actions, fund movement, data deletion, or
  secret exposure.

## GitHub Supervision Contract

- ChatGPT writes or updates `TASK_QUEUE.md` on GitHub.
- The Mac mini worker pulls `main`, reads `TASK_QUEUE.md`, executes safe work, updates status files, commits, and pushes back to GitHub.
- `STATUS.md` is the current state surface.
- `RUN_LOG.md` is the execution record.
- `DECISION_REQUIRED.md` is the human-confirmation queue.
- `RISK_CONTROL.md` is the binding risk boundary.
- The established GPT-Codex GitHub route is recorded in `PROJECT_MEMORY.md` and `.codex/skills/gpt-codex-github-handoff/SKILL.md`.

## Stop Conditions

Stop immediately and write `DECISION_REQUIRED.md` if a task involves:

- Real trading
- Real order placement
- Real order cancellation
- Real broker login or permission changes
- Fund transfer
- Margin movement
- Deleting original/raw data
- Secret/key/password exposure
- `danger-full-access`
- System-level modification outside this project
- Large paid API/cloud calls

### Current supervision (2026-09-22)
The native Codex heartbeat `GitHub 本机任务接收与执行` is active every 10 minutes in the local takeover task. Following the owner's explicit 2026-09-22 request, it now claims and executes new owner-authored, authorized, safe local tasks submitted to TASK_QUEUE.md, then writes real pickup and completion/failure receipts. It does not revive the legacy shell worker or execute old TASK-033. It reviews source and scope, prevents duplicate execution, and stops at actual safety/authorization boundaries. Unchanged polling is silent. A queued task is not running until its fresh pickup receipt exists. Scheduled execution was verified by the actual native heartbeat on 2026-09-22: TASK-035 pickup, local macOS execution, and GitHub receipt writeback succeeded. See REPORTS/native_dispatch_smoke_20260922.md. Historical claims above do not revive the retired shell worker.
