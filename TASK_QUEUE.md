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
- Result: LOCAL_WORKER_MAIL_SENT

### TASK-023-LOCAL-MAIL-DELIVERY-VERIFY
- Status: pending
- Type: local_status_check
- Title: Local worker mail delivery verification
- Request: Send one local mail test to the private default recipient configured on the Mac mini. Use subject marker `CODEX-DELIVERY-TEST-20260629-2030`. Do not write recipient values. Do not print local configuration. After sending, check local mail queue, local send result, and any local bounce or failure signal available to the worker. Update `GPT_CODEX_CONVERSATION.md`, `STATUS.md`, and `RUN_LOG.md` with one of: `LOCAL_WORKER_MAIL_DELIVERY_SENT`, `LOCAL_WORKER_MAIL_QUEUED`, `LOCAL_WORKER_MAIL_BOUNCED`, `LOCAL_WORKER_MAIL_FAILED`, or `LOCAL_WORKER_MAIL_NO_DEFAULT_RECIPIENT`. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: The user-visible status shows the subject marker and one of the delivery status markers without exposing recipient data.
- Safety: repository_status_only
- Created: 2026-06-29
- Result:
