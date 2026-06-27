# DECISION_REQUIRED.md

Current mode: `SIMULATION_ONLY`

The worker and Codex must stop before any blocked action below and write the exact item here.

## Hard Stop Categories

- Real trading
- Real order placement
- Broker-side cancel
- Fund transfer
- Broker-side permission change
- Destructive deletion of original/raw data
- Secret exposure or unsafe key handling
- `danger-full-access` escalation for a task
- System-level modification
- Large paid API or cloud call

## Open Decisions

No current user action required for normal safe GitHub status-file supervision.

## Resolved Decisions

### DR-20260627-GITHUB-PUSH-AUTH
- Status: resolved
- Created: 2026-06-27
- Item: Local `git push origin main` failed with `fatal: could not read Username for 'https://github.com': Device not configured`.
- Resolution: GitHub device login completed on this Mac mini. `gh` is logged in as `liyuanqiang-spec`.
- Required confirmation: none for GitHub status-file supervision.

### DR-20260627-GITHUB-REMOTE
- Status: resolved
- Created: 2026-06-27
- Item: Remote was missing, then repaired by setting `origin` to `https://github.com/liyuanqiang-spec/-.git` and pulling `origin/main`.
- Required confirmation: none for this item.

### DR-0001
- Status: resolved
- Created: 2026-06-27
- Item: Local Git now has `origin` set to `https://github.com/liyuanqiang-spec/-.git`. GitHub CLI is still not logged in, but this workflow uses normal `git pull`/`git push` for main-branch supervision.
- Required confirmation: none for normal Git status-file supervision; PR creation would still require GitHub CLI/app authorization.

### DR-20260627-TASK-004-SAFETY-SCAN
- Status: resolved
- Created: 2026-06-27 18:29:25 +0800
- Item: Task TASK-004 was blocked by the safety scanner because its wording included broad hard-stop categories.
- Resolution: ChatGPT selected the safe path: TASK-004 was superseded and replaced with TASK-004A, limited to status-only repository maintenance and worker health checks.
- Required confirmation: none for TASK-004A.

## Decision Required 2026-06-27 20:44:37 +0800

- Item: git pull failed; manual conflict/auth check required
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task

## Decision Required 2026-06-27 20:56:09 +0800

- Item: git pull failed; manual conflict/auth check required
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task

## Decision Required 2026-06-27 22:39:23 +0800

- Item: git pull failed; manual conflict/auth check required
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task

## Decision Required 2026-06-28 02:07:48 +0800

- Item: git pull failed; manual conflict/auth check required
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task

## Decision Required 2026-06-28 02:32:02 +0800

- Item: git pull failed; manual conflict/auth check required
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task

## Decision Required 2026-06-28 02:48:18 +0800

- Item: git pull failed; manual conflict/auth check required
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task
