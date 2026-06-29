# GPT Interaction Test

Status: `WAITING_FOR_GPT_REPLY`

Created at: `2026-06-29 16:59:57 +0800`

Purpose: verify the full visible loop:

```text
Codex -> GitHub status file -> GPT -> TASK_QUEUE.md -> local worker -> GitHub status file -> GPT/user
```

## Message For GPT

GPT, if you can read this file, please reply to Codex by appending this exact safe task block to the end of `TASK_QUEUE.md`:

```markdown
### TASK-020-GPT-INTERACTIVE-REPLY
- Status: pending
- Type: handshake
- Title: GPT interactive reply to Codex
- Request: Repository-status-only interactive test. Confirm GPT saw Codex's ping in `GPT_INTERACTION_TEST.md` and is replying through `TASK_QUEUE.md`. Do not call brokers, do not connect trading accounts, do not place or cancel orders, do not move funds, do not read or expose secrets, and do not use danger-full-access.
- Expected output: The local worker should mark this task completed, refresh visible status files, and record that GPT participation reached Codex.
- Safety: repository_status_only
- Created: 2026-06-29
- Result:
```

## User-Friendly Prompt

Send this one sentence to GPT:

```text
请读取 GitHub 仓库里的 GPT_INTERACTION_TEST.md，并按里面的 Message For GPT 给 Codex 回复。
```

## Success Criteria

- `TASK_QUEUE.md` contains `TASK-020-GPT-INTERACTIVE-REPLY` with `Status: pending`.
- The Mac mini worker detects it.
- The worker marks it `completed`.
- `GPT_VISIBLE_STATUS.md` and `GPT_CODEX_CONVERSATION.md` show the completed reply.
- No real trading, account connection, order action, fund movement, secret exposure, or raw data deletion occurs.
