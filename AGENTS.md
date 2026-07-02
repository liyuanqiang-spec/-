# AGENTS.md

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
