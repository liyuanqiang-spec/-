# TASK_QUEUE.md

This queue is the GitHub handoff channel from GPT to the local worker.

Worker rule: execute the first task whose Status is `pending` and whose Safety is safe. Do not repeat completed tasks.

## Tasks

### TASK-019A
- Status: completed
- Type: status_check
- Title: Verify local supervisor loop
- Result: GPT handshake completed by local worker

### TASK-020-GPT-INTERACTIVE-REPLY
- Status: decision_required
- Type: handshake
- Title: GPT interactive reply to local worker
- Result: blocked by local guard

### TASK-021-LOCAL-MAIL-SMOKE
- Status: pending
- Type: local_status_check
- Title: Local worker visible smoke check
- Request: Run the existing local mail smoke path from the Mac mini worker if it is available. Use only locally configured recipient data. Do not write recipient data into the repo. Do not print local configuration. Then update GPT_CODEX_CONVERSATION.md with one of these exact statuses: LOCAL_WORKER_MAIL_SENT, LOCAL_WORKER_MAIL_SKIPPED_NO_RECIPIENT, or LOCAL_WORKER_MAIL_FAILED. Also mark this task completed or decision_required.
- Expected output: GPT_CODEX_CONVERSATION.md clearly shows GPT requested the local worker check and the local worker replied with SENT, SKIPPED, or FAILED.
- Safety: repository_status_only
- Created: 2026-06-29
- Result:
