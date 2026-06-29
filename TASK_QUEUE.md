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
- Status: superseded
- Type: handshake
- Title: GPT interactive reply to local worker
- Result: superseded by TASK-021 and TASK-022 local visible/mail smoke checks

### TASK-021-LOCAL-MAIL-SMOKE
- Status: completed
- Type: local_status_check
- Title: Local worker visible smoke check
- Result: LOCAL_WORKER_MAIL_SKIPPED_NO_RECIPIENT

### TASK-022-LOCAL-MAIL-RETRY
- Status: completed
- Type: local_status_check
- Title: Local worker mail retry
- Request: Run the local mail smoke path again. If the worker has a previous successful local mail-test recipient available in its own local history or repo-visible prior status, reuse that same recipient without printing it. Do not write recipient values. Do not print local configuration. Update GPT_CODEX_CONVERSATION.md with LOCAL_WORKER_MAIL_SENT or LOCAL_WORKER_MAIL_FAILED. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: GPT_CODEX_CONVERSATION.md shows the local worker reply as LOCAL_WORKER_MAIL_SENT or LOCAL_WORKER_MAIL_FAILED, and TASK_QUEUE.md marks this task completed or decision_required.
- Safety: repository_status_only
- Created: 2026-06-29
- Result: codex exec completed
