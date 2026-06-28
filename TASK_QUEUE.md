# TASK_QUEUE.md

This queue is the GitHub handoff channel from ChatGPT to the local worker.

Worker rule: execute the first task whose Status is `pending` and whose Safety is safe. Do not repeat completed tasks.

## Tasks

### TASK-000-GPT-HANDSHAKE
- Status: completed
- Type: status_check
- Title: GPT to local worker handshake
- Result: GPT_HANDSHAKE_OK recorded.

### TASK-001
- Status: completed
- Type: development
- Title: MVP scaffold initialization
- Result: completed by worker.

### TASK-002
- Status: completed
- Type: data_schema
- Title: Data schema standardization
- Result: completed by worker.

### TASK-003
- Status: completed
- Type: research
- Title: Low-liquidity contract scan
- Result: completed by worker.

### TASK-004
- Status: superseded
- Type: worker_stability
- Title: Original worker stability task
- Result: superseded by TASK-004A.

### TASK-004A
- Status: completed
- Type: worker_stability_status_only
- Title: Stabilize local worker status loop
- Result: completed by worker.

### TASK-005
- Status: completed
- Type: dashboard
- Title: Create worker dashboard
- Result: completed by worker.

### TASK-006
- Status: completed
- Type: worker_stability_status_only
- Title: Change idle poll interval to 10 minutes
- Result: codex exec completed.

### TASK-007
- Status: completed
- Type: simulation_development
- Title: Build first complete simulation version for silver option liquidity radar
- Result: codex exec completed.

### TASK-008
- Status: completed
- Type: repo_status_setup
- Title: Finish GPT visible status layer
- Request: Complete the repository status layer using the files already created by ChatGPT. Refresh GPT_VISIBLE_STATUS.md, GPT_REVIEW.md, .gpt_state.json, and WORKER_DASHBOARD.md. Keep work limited to repository status, planning, tests, and simulation-only reporting.
- Expected output: refreshed visible status, review log note, state file, dashboard, tests.
- Safety: repository_status_only
- Created: 2026-06-28
- Last update: completed by Codex 2026-06-28 12:38:15 +0800
- Result: TASK-008 completed; GPT visible status layer, worker dashboard refresh, structured state file, health check, and worker reporting hooks stabilized.

### TASK-009
- Status: pending
- Type: project_software_update
- Title: Safe repository software update baseline
- Request: Perform a repository-only software update pass. Read RELIABILITY_RUNBOOK.md first. Inventory Python modules, tests, scripts, reports, and dependency files. Update only project code, tests, documentation, and repository-local configuration where needed. Preserve the visible status flow. Run health checks and test commands. Write a concise upgrade report in REPORTS/software_update_baseline.md.
- Expected output: updated repository code or documentation as needed, software update baseline report, refreshed dashboard, refreshed GPT visible status, passing health checks and tests.
- Safety: repository_only
- Created: 2026-06-28
- Last update: created by ChatGPT after TASK-008 completion
- Result: pending
