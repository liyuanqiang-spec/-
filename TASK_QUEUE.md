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
- Status: running
- Type: local_status_check
- Title: Local worker mail delivery verification
- Request: Send one local mail test to the private default recipient configured on the Mac mini. Use subject marker `CODEX-DELIVERY-TEST-20260629-2030`. Do not write recipient values. Do not print local configuration. After sending, check local mail queue, local send result, and any local bounce or failure signal available to the worker. Update `GPT_CODEX_CONVERSATION.md`, `STATUS.md`, and `RUN_LOG.md` with one of: `LOCAL_WORKER_MAIL_DELIVERY_SENT`, `LOCAL_WORKER_MAIL_QUEUED`, `LOCAL_WORKER_MAIL_BOUNCED`, `LOCAL_WORKER_MAIL_FAILED`, or `LOCAL_WORKER_MAIL_NO_DEFAULT_RECIPIENT`. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: The user-visible status shows the subject marker and one of the delivery status markers without exposing recipient data.
- Safety: repository_status_only
- Created: 2026-06-29
- Result: worker started

### TASK-024-ADOPT-GPT-CODEX-PROTOCOL
- Status: pending
- Type: repo_status_setup
- Title: Adopt GPT Codex communication protocol
- Request: Read `GPT_CODEX_PROTOCOL.md` and `CODEX_GROUP_CHAT.md`. Update the repository status layer so future worker results append concise role-tagged messages to `CODEX_GROUP_CHAT.md` and keep `GPT_CODEX_CONVERSATION.md` user-facing. Do not change quant strategy logic or data. Keep this to repository status files and lightweight reporting scripts. Preserve PHASE_1_SIMULATION_ONLY.
- Expected output: `CODEX_GROUP_CHAT.md` has at least one Codex-Core reply confirming adoption, `GPT_CODEX_CONVERSATION.md` references the protocol, `STATUS.md` and `RUN_LOG.md` note protocol adoption, and TASK-024 is marked completed or decision_required.
- Safety: repository_status_only
- Created: 2026-06-29
- Result:
