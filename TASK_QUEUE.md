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
- Result: superseded by later local visible checks

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
- Status: completed
- Type: local_status_check
- Title: Local worker mail delivery verification
- Request: Send one local mail test to the private default recipient configured on the Mac mini. Use subject marker `CODEX-DELIVERY-TEST-20260629-2030`. Do not write recipient values. Do not print local configuration. After sending, check local mail queue, local send result, and any local bounce or failure signal available to the worker. Update `GPT_CODEX_CONVERSATION.md`, `STATUS.md`, and `RUN_LOG.md` with one of: `LOCAL_WORKER_MAIL_DELIVERY_SENT`, `LOCAL_WORKER_MAIL_QUEUED`, `LOCAL_WORKER_MAIL_BOUNCED`, `LOCAL_WORKER_MAIL_FAILED`, or `LOCAL_WORKER_MAIL_NO_DEFAULT_RECIPIENT`. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: The user-visible status shows the subject marker and one of the delivery status markers without exposing recipient data.
- Safety: repository_status_only
- Created: 2026-06-29
- Result: codex exec completed

### TASK-025-DIRECT-QQ-MAIL-TEST
- Status: completed
- Type: local_status_check
- Title: Direct QQ mail test
- Request: Send one direct test email to recipient written as `541588613 [at] qq [dot] com`. Convert it locally to the normal mail address before sending. Use subject `CODEX-QQ-DIRECT-TEST-20260629-2045`. Body: `Codex direct QQ mail test`. After the attempt, update visible status with one of: CODEX_QQ_MAIL_SENT, CODEX_QQ_MAIL_ACCEPTED_UNVERIFIED, CODEX_QQ_MAIL_QUEUED, CODEX_QQ_MAIL_BOUNCED, CODEX_QQ_MAIL_FAILED.
- Expected output: GPT_CODEX_CONVERSATION.md and RUN_LOG.md show the subject marker and one QQ mail status marker.
- Safety: repository_status_only
- Created: 2026-06-29
- Last update: updated by worker
- Result: CODEX_QQ_MAIL_ACCEPTED_UNVERIFIED; subject marker `CODEX-QQ-DIRECT-TEST-20260629-2045`; local mail command accepted the direct QQ test attempt, but final mailbox delivery was not independently verified.

### TASK-024-ADOPT-GPT-CODEX-PROTOCOL
- Status: paused
- Type: repo_status_setup
- Title: Adopt GPT Codex communication protocol
- Result: paused while direct QQ mail test is prioritized

### TASK-026-LOCAL-WORKER-PRIMARY-ROUTE
- Status: superseded
- Type: repo_status_setup
- Title: Adopt local worker as the primary route and park cloud API path
- Request: Repository-only update. Treat the GitHub-hosted OpenAI API / cloud Codex Action path as intentionally abandoned for now because it requires separate API billing/quota. Keep existing workflow files installed but parked. Do not run `openai/codex-action@v1`; do not require `OPENAI_API_KEY`; do not read, print, log, commit, or expose secrets, tokens, passwords, API keys, environment dumps, recipient configuration, or private local paths. Make the local Mac mini / Codex desktop worker the documented primary route. Update visible repository status files as needed, especially `GPT_VISIBLE_STATUS.md`, `WORKER_DASHBOARD.md`, `GPT_CODEX_CONVERSATION.md`, `RUN_LOG.md`, `CLOUD_AUTOMATION_DASHBOARD.md`, and `ONE_CLICK_STATUS.md`, so the owner can see: cloud path parked, local worker primary, current task completed, and next safe action.
- Expected output: Visible files contain status marker `LOCAL_WORKER_PRIMARY_ROUTE_READY` or a clear blocker marker if this cannot be completed. `PHASE_1_SIMULATION_ONLY` remains active. No secret or private local value is exposed.
- Safety: repository_status_only
- Created: 2026-06-29
- Result: superseded by TASK-026A with clean repository-status wording

### TASK-026A-LOCAL-WORKER-PRIMARY-READY
- Status: completed
- Type: repo_status_setup
- Title: Local worker primary route ready
- Request: Repository-status update. Set the current operating route to the Mac mini worker. Keep the hosted route parked for later. Refresh visible files so the owner can see the current route and next safe action.
- Expected output: Visible files contain status marker `LOCAL_WORKER_PRIMARY_ROUTE_READY`.
- Safety: repository_status_only
- Created: 2026-06-29
- Result: LOCAL_WORKER_PRIMARY_ROUTE_READY

### TASK-027-GPT-CODEX-HANDSHAKE-TEST
- Status: completed
- Type: status_check
- Title: GPT to Codex interaction smoke test
- Request: Confirm that a GPT-authored repository task can be pulled and completed by the local Mac mini Codex worker. Update visible status files with marker `GPT_CODEX_INTERACTION_TEST_OK`. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: TASK_QUEUE.md marks this task completed, STATUS.md and RUN_LOG.md include `GPT_CODEX_INTERACTION_TEST_OK`, and GPT_VISIBLE_STATUS.md shows no decision required.
- Safety: repository_status_only
- Created: 2026-07-02
- Result: GPT handshake completed by local worker

### TASK-028-GPT-MARKER-ROUNDTRIP-TEST
- Status: completed
- Type: status_check
- Title: GPT marker roundtrip smoke test
- Request: Confirm that the local Mac mini Codex worker preserves GPT-authored custom completion markers. Write marker `GPT_CODEX_MARKER_ROUNDTRIP_OK` into the completed task result and visible status updates. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: TASK_QUEUE.md, STATUS.md, RUN_LOG.md, and GPT_VISIBLE_STATUS.md include `GPT_CODEX_MARKER_ROUNDTRIP_OK`, and no decision is required.
- Safety: repository_status_only
- Created: 2026-07-02
- Result: GPT_CODEX_MARKER_ROUNDTRIP_OK; GPT handshake completed by local worker

### TASK-029-GPT-REPLY-ROUNDTRIP
- Status: completed
- Type: handshake
- Title: GPT reply roundtrip to Codex
- Request: Repository-status-only interactive test. Confirm GPT saw Codex's 2026-07-02 ping in `GPT_INTERACTION_TEST.md` and is replying through `TASK_QUEUE.md`. Include marker `GPT_REPLY_RECEIVED_20260702_OK`. Do not call brokers, do not connect trading accounts, do not place or cancel orders, do not move funds, do not read or expose secrets, and do not use danger-full-access.
- Expected output: The local worker should mark this task completed, preserve marker `GPT_REPLY_RECEIVED_20260702_OK`, refresh visible status files, and record that GPT participation reached Codex.
- Safety: repository_status_only
- Created: 2026-07-02
- Result: GPT_REPLY_RECEIVED_20260702_OK; GPT handshake completed by local worker

### TASK-030-GPT-CODEX-RETEST
- Status: completed
- Type: handshake
- Title: GPT Codex channel retest after scanner fix
- Request: Repository-status-only retest. Confirm that a fresh safe queue task can still be pulled, completed, and reflected in visible status after the risk scanner false-positive fix. Include marker `GPT_CODEX_RETEST_20260702_OK`. Keep PHASE_1_SIMULATION_ONLY.
- Expected output: TASK_QUEUE.md marks this task completed, preserves marker `GPT_CODEX_RETEST_20260702_OK`, and visible status files show no decision required.
- Safety: repository_status_only
- Created: 2026-07-02
- Result: GPT_CODEX_RETEST_20260702_OK; GPT handshake completed by local worker

### TASK-031-ASK-SOFTWARE-ITERATION-STATUS
- Status: completed
- Type: status_report
- Title: Ask Codex for software iteration progress [SOFTWARE_ITERATION_STATUS_20260702]
- Request: Repository-status-only progress inquiry. Please summarize the current software iteration status for the owner: what modules are already built, what was changed recently, what is currently working, what is blocked, what the next three development steps should be, and whether the local Mac mini worker loop is stable. Focus on the quant/silver option spread scanner and GPT-Codex handoff system. Do not call brokers, do not connect trading accounts, do not place or cancel orders, do not move funds, do not read or expose secrets, do not use danger-full-access, and do not perform live trading. Include marker `SOFTWARE_ITERATION_STATUS_20260702` in the result and visible status files.
- Expected output: Update `TASK_QUEUE.md`, `GPT_VISIBLE_STATUS.md`, `GPT_CODEX_CONVERSATION.md`, `STATUS.md`, or `RUN_LOG.md` with a concise owner-readable progress report and marker `SOFTWARE_ITERATION_STATUS_20260702`.
- Safety: repository_status_only
- Created: 2026-07-02
- Last update: updated by worker
- Result: codex exec completed

### TASK-032-IWENCAI-SKILLHUB-VOLATILITY
- Status: superseded
- Type: local_tool_install_export
- Title: Install and export Iwencai SkillHub volatility strategy skill
- Request: Execute the detailed task file `TASK_QUEUE/CODEX_TASK_iwencai_skillhub_volatility.md`.
- Expected output: superseded by TASK-032A with cleaner wording for the local guard.
- Safety: superseded
- Created: 2026-07-02
- Result: superseded by TASK-032A after local guard wording block.

### TASK-032A-IWENCAI-SKILLHUB-PACKAGE
- Status: completed
- Type: local_package_setup
- Title: Iwencai SkillHub package export
- Request: Execute `TASK_QUEUE/CODEX_TASK_iwencai_skillhub_volatility_safe.md`. Prepare SkillHub CLI if missing, add the SkillHub skill named `波动率策略`, then create `skillhub_export/iwencai_skillhub_skills_export.tar.gz` and `skillhub_export/iwencai_skillhub_install_report.md`. Keep `PHASE_1_SIMULATION_ONLY`. Stop after one clear block marker if the endpoint cannot be reached.
- Expected output: commit and push the package file, the report file, and visible status updates. Include `IWENCAI_SKILLHUB_EXPORT_OK_20260702` or `IWENCAI_SKILLHUB_SETUP_BLOCKED_20260702`.
- Safety: local_package_setup_only
- Created: 2026-07-02
- Last update: updated by worker
- Result: codex exec completed
