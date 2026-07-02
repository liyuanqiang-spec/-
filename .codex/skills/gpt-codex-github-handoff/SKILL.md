# GPT-Codex GitHub Handoff Skill

## Purpose

This skill records the working communication route between ChatGPT and the local Mac mini Codex worker.

Use this skill whenever the owner asks ChatGPT to instruct Codex, check Codex progress, push a task to Codex, retrieve Codex output, or continue the supervised quant/software workflow.

## Known working route

- Repository: `liyuanqiang-spec/-`
- Default branch: `main`
- Git remote: `https://github.com/liyuanqiang-spec/-.git`
- Primary queue: `TASK_QUEUE.md`
- Optional detailed task files: `TASK_QUEUE/*.md`
- Current-state file: `STATUS.md`
- Execution log: `RUN_LOG.md`
- User-visible status: `GPT_VISIBLE_STATUS.md`
- GPT/Codex conversation ledger: `GPT_CODEX_CONVERSATION.md`
- Human decision queue: `DECISION_REQUIRED.md`
- Risk boundary: `RISK_CONTROL.md`

## Contract

ChatGPT does not directly control the user's local Codex session. ChatGPT communicates with Codex by writing safe tasks into GitHub.

The local Mac mini worker pulls `main`, reads `TASK_QUEUE.md`, executes the first pending safe task, updates visible status/log files, commits, and pushes back.

The worker has previously completed multiple handshake tasks, including markers such as:

- `GPT_CODEX_INTERACTION_TEST_OK`
- `GPT_CODEX_MARKER_ROUNDTRIP_OK`
- `GPT_REPLY_RECEIVED_20260702_OK`
- `GPT_CODEX_RETEST_20260702_OK`

Therefore, when the owner says "you and Codex can communicate through Git", treat this route as established unless repository access fails.

## Standard ChatGPT procedure

When the owner asks ChatGPT to send work to Codex:

1. Use GitHub connector access to `liyuanqiang-spec/-`.
2. Read `TASK_QUEUE.md` and, when needed, `STATUS.md`, `RUN_LOG.md`, and `GPT_VISIBLE_STATUS.md`.
3. Append a new `TASK-###` to `TASK_QUEUE.md` with:
   - `Status: pending`
   - task type
   - concise title
   - clear request
   - expected output
   - safety boundary
   - created date
4. For complex tasks, create a detailed task file under `TASK_QUEUE/` and reference it from `TASK_QUEUE.md`.
5. Include explicit hard stops: no live trading, no broker connection, no order placement/cancellation, no fund movement, no secret exposure, no `danger-full-access`.
6. After Codex pushes results, fetch the relevant files from GitHub and summarize the result for the owner.

## Standard Codex worker procedure

When running locally, Codex should:

1. Pull the latest `main`.
2. Read `AGENTS.md`, `RISK_CONTROL.md`, `PROJECT_MEMORY.md`, and this skill.
3. Execute the first `pending` task in `TASK_QUEUE.md` only if safety is acceptable.
4. Update task status and result in `TASK_QUEUE.md`.
5. Update `STATUS.md`, `RUN_LOG.md`, and `GPT_VISIBLE_STATUS.md` when present.
6. Commit and push outputs.
7. Never write secrets, API keys, passwords, tokens, local private configs, trading account details, or recipient values into the repository.

## Safety defaults

Current operating phase remains:

```text
PHASE_1_SIMULATION_ONLY
```

Allowed by default:

- software development
- safe CLI installation for tooling
- data processing
- research
- backtesting
- simulated trading
- reports
- repository-status updates

Forbidden by default:

- real broker login
- real order placement
- real order cancellation
- fund movement
- margin movement
- exposing secrets
- destructive deletion of original/raw data
- `danger-full-access`

## Owner-preferred response style

When reporting to the owner, use short Chinese conclusions first. Then give only necessary evidence, file names, markers, and next action.

## Reuse trigger phrases

Use this skill when the owner says or implies:

- "给 Codex 发指令"
- "通过 Git 跟 Codex 沟通"
- "看 Codex 进展"
- "让 Codex 安装/下载/执行"
- "你们路径打通了吗"
- "继续让 Codex 做"
- "用之前测试过的链路"
- "本地 worker"
- "Mac mini worker"
