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
- Status: pending
- Type: repo_automation_setup
- Title: Add GPT review automation layer
- Request: Add the repository automation layer that lets GPT review completed worker output and append the next safe task. Create or update: `.github/workflows/gpt_orchestrator.yml`, `scripts/gpt_orchestrator.py`, `GPT_REVIEW.md`, `GPT_VISIBLE_STATUS.md`, and `.gpt_state.json`. The workflow should support manual run and a 10-minute schedule. The script should read PROJECT_MEMORY.md, TASK_QUEUE.md, STATUS.md, RUN_LOG.md, WORKER_DASHBOARD.md, DECISION_REQUIRED.md, and REPORTS. If there is already a pending or running task, update GPT_VISIBLE_STATUS.md only and do not run the model. If no task is pending, run the model review, append GPT_REVIEW.md, optionally append one next safe task to TASK_QUEUE.md, update GPT_VISIBLE_STATUS.md, and store state to avoid repeated reviews. Use the repository Actions setting named OPENAI_API_KEY and optional OPENAI_MODEL. If the setting is absent, write NEEDS_OPENAI_API_KEY to GPT_VISIBLE_STATUS.md and exit cleanly. Keep this layer limited to review, planning, and queue updates.
- Expected output: workflow file, orchestration script, GPT review log, visible GPT status page, state file, README or dashboard link if practical, STATUS.md and RUN_LOG.md setup notes.
- Safety: repo_automation_only
- Created: 2026-06-28
- Last update: created by ChatGPT
- Result: pending
