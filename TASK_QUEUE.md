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
- Result: TASK-008 completed; visible status layer and worker reporting hooks stabilized.

### TASK-009
- Status: completed
- Type: quant_system_enhancement
- Title: Build quant system enhancement baseline
- Result: completed; generated quant gap report, backtest baseline report, replay CSV, time-value radar, scoring/state-machine replay baseline, and tests.

### TASK-010
- Status: completed
- Type: quant_replay_data
- Title: Add multi-snapshot option quote replay fixture and loader
- Result: completed; added repository-local multi-snapshot quote replay fixture, replay loader, deterministic stale quote/timeout/incomplete-leg tests, and refreshed baseline replay reports. Git result sync was rebased and recorded in the queue.

### TASK-011
- Status: superseded
- Type: local_tqsdk_tick_validation
- Title: Original local TqSdk smoke test wording
- Result: superseded by TASK-011A because the worker risk scanner stopped on overly broad wording.

### TASK-011A
- Status: completed
- Type: offline_tick_file_validation
- Title: Validate local historical tick files with offline replay adapter
- Result: completed; added offline tick adapter, validation script, sanitized non-performance tick fixture, tick smoke report, refreshed quant reports, and passed 21 tests.

### TASK-012
- Status: completed
- Type: worker_cost_control
- Title: Reduce idle worker calls and writes
- Result: codex exec completed.

### TASK-013
- Status: decision_required
- Type: auto_review_workflow
- Title: Build visible GPT auto-review trigger
- Result: blocked by risk control.

### TASK-013A
- Status: completed
- Type: visible_review_scaffold
- Title: Build safe visible review scaffold
- Request: Create a repository-only visible review scaffold without network calls. Add a scheduled and manual GitHub workflow file that runs a local Python script. Add `scripts/visible_review_scaffold.py`. The script should read PROJECT_MEMORY.md, TASK_QUEUE.md, STATUS.md, RUN_LOG.md, WORKER_DASHBOARD.md, GPT_VISIBLE_STATUS.md, DECISION_REQUIRED.md, REPORTS, src, and tests summaries. It should write or refresh GPT_REVIEW.md and GPT_VISIBLE_STATUS.md with a clear state: SCAFFOLD_READY, WORKER_BUSY, or FAILED_WITH_REASON. It must not call outside services. It must not read or print sensitive values. It must not edit strategy code or data. It must only summarize repository status and next safe human-supervision action.
- Expected output: workflow file, local scaffold script, refreshed GPT_REVIEW.md, refreshed GPT_VISIBLE_STATUS.md, state file if useful, STATUS/RUN_LOG notes, and passing syntax checks.
- Safety: repository_status_only
- Created: 2026-06-28
- Result: codex exec completed.

### TASK-014
- Status: decision_required
- Type: visible_status_alignment
- Title: Show scaffold readiness in GPT visible status
- Request: Keep this repository-status-only. Update the visible review scaffold so `GPT_VISIBLE_STATUS.md` displays the scaffold state explicitly when the scaffold is ready. The file should show `SCAFFOLD_READY` when `GPT_REVIEW.md` has a successful visible-review scaffold block, `WORKER_BUSY` when a safe worker task is running, and `FAILED_WITH_REASON` when the local scaffold check fails. Do not call outside services. Do not read or print secrets. Do not edit strategy code, trading logic, data, or reports except the status/review files. Refresh `GPT_VISIBLE_STATUS.md`, `GPT_REVIEW.md`, `WORKER_DASHBOARD.md`, `STATUS.md`, and `RUN_LOG.md`.
- Expected output: visible status clearly includes `SCAFFOLD_READY`, updated scaffold script if needed, refreshed visible files, and passing syntax checks.
- Safety: repository_status_only
- Created: 2026-06-28
- Result: blocked by risk control.

### TASK-014A
- Status: completed
- Type: status_display_patch
- Title: Add scaffold state line to visible status
- Request: Repository-status-only patch. Adjust the existing visible review script so `GPT_VISIBLE_STATUS.md` includes one line named `Visible scaffold:` with one of these values: `SCAFFOLD_READY`, `WORKER_BUSY`, or `FAILED_WITH_REASON`. Use only existing local repository status and review files as inputs. If `GPT_REVIEW.md` already contains a successful scaffold block and no current worker task is active, write `SCAFFOLD_READY`. Refresh `GPT_VISIBLE_STATUS.md`, `GPT_REVIEW.md`, `WORKER_DASHBOARD.md`, `STATUS.md`, and `RUN_LOG.md`. Keep changes limited to status/review/reporting files and the status script. Run syntax checks.
- Expected output: visible status includes a clear `Visible scaffold:` line, review file refreshed, dashboard/status/log refreshed, syntax checks pass.
- Safety: repository_status_only
- Created: 2026-06-28
- Result: codex exec completed

### TASK-015
- Status: pending
- Type: adaptive_worker_polling
- Title: Add adaptive polling frequency for local GitHub worker
- Safety: repository_status_only
- Created: 2026-06-28

## Objective

Improve the local Mac mini GitHub worker polling logic so it reacts faster when activated, then automatically reduces frequency after several idle checks.

Do not edit strategy code, trading logic, broker/API code, account code, order code, fund movement code, secrets, raw market data, or production trading files.

This task is only about worker scheduling, status files, and repository supervision.

## Required behavior

Implement adaptive polling in the local worker loop:

1. **Active mode**
   - When the worker finds a pending safe task, starts executing a task, or detects `WORKER_BUSY`, poll frequently.
   - Suggested active interval: `30s` or `60s`.
   - During active execution, update status files normally.

2. **Warm mode**
   - After a task completes, fails safely, or writes a blocker, keep higher frequency for a short period.
   - Suggested warm interval: `60s`.
   - Stay in warm mode for about `3` consecutive checks.

3. **Idle mode**
   - If there are no pending safe tasks and no unresolved blocker for several consecutive checks, automatically reduce frequency.
   - Suggested idle interval: `600s`.
   - Enter idle mode after `5` consecutive idle checks.

4. **Immediate reactivation**
   - If any new pending safe task appears in `TASK_QUEUE.md`, immediately switch back to active mode.
   - If `DECISION_REQUIRED.md` has a new unresolved blocker, switch to warm mode and surface it in visible status.

5. **Visible status**
   - Update `GPT_VISIBLE_STATUS.md` to show:
     - current worker mode: `ACTIVE`, `WARM`, or `IDLE`
     - current poll interval
     - consecutive idle count
     - latest completed task
     - unresolved blocker, if any
     - next executable action

6. **Dashboard**
   - Update `WORKER_DASHBOARD.md` to include the adaptive polling state.
   - It should be obvious whether the worker is sleeping long because it is truly idle.

7. **Run log**
   - Append clear notes to `RUN_LOG.md` when:
     - active mode starts
     - warm mode starts
     - idle mode starts
     - interval changes
     - blocker detected
     - new pending task detected

8. **Configuration**
   - Put polling parameters in one clearly editable place, for example:
     - `ACTIVE_POLL_SECONDS=30`
     - `WARM_POLL_SECONDS=60`
     - `IDLE_POLL_SECONDS=600`
     - `IDLE_BACKOFF_AFTER_CHECKS=5`
     - `WARM_CHECKS_AFTER_ACTIVITY=3`
   - Prefer environment variables with safe defaults, or a small config section inside the worker script.

9. **Safety scanner**
   - Keep existing safety scanner behavior.
   - Do not weaken risk controls.
   - If a task is unsafe, do not execute it. Mark it blocked and write a clear reason.

10. **No external service calls**
   - Do not call brokers, exchanges, trading software, financial accounts, or outside services.
   - Normal GitHub pull/commit/push for repository status synchronization is allowed if already used by the worker.

## Expected output

- Updated worker polling logic.
- Updated status/dashboard/reporting files:
  - `GPT_VISIBLE_STATUS.md`
  - `WORKER_DASHBOARD.md`
  - `STATUS.md`
  - `RUN_LOG.md`
  - `DECISION_REQUIRED.md` only if a real unresolved decision exists.
- Passing syntax checks.
- A short note in `TASK_QUEUE.md` marking this task completed when done.

## Acceptance criteria

The task is complete only when:

1. Worker can run in adaptive modes: `ACTIVE`, `WARM`, `IDLE`.
2. New safe pending task causes high-frequency polling.
3. Several idle checks automatically reduce polling frequency.
4. `GPT_VISIBLE_STATUS.md` clearly exposes mode and interval.
5. No trading, account, broker, secret, raw data, or unsafe action is touched.
6. The repo is committed and pushed successfully.
