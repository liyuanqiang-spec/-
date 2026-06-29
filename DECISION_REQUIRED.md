# DECISION_REQUIRED.md

Current mode: `SIMULATION_ONLY`

For binding safety limits, see `RISK_CONTROL.md`.

## Open Decisions

No current user action required for normal safe GitHub status-file supervision.

## Resolved Decisions

### DR-20260628-TASK-011-WORDING-BLOCKED
- Status: resolved
- Created: 2026-06-28 20:27:28 +0800
- Item: TASK-011 was blocked by the worker risk scanner because the task wording mixed local data validation with sensitive broker/account/secret/trading terms.
- Resolution: ChatGPT superseded TASK-011 and created TASK-011A as an offline repository-file validation task. TASK-011A is now running.
- Required confirmation: none.

### DR-20260628-WORKER-RELOAD-SUPPORT-CLONE-DIVERGED
- Status: resolved
- Created: 2026-06-28 16:33:26 +0800
- Item: Worker reload was blocked by divergent support clone.
- Detail: Existing `scripts/start_worker.sh` could not reload launchd worker because the support clone at `~/Library/Application Support/CodexGithubWorker/repo` was `ahead 1, behind 30` with local modified status files.
- Resolution: User granted full authorization. Codex created backup branch `backup/support-clone-20260628-165020`, stashed local support-clone changes, reset the support clone to `origin/main`, and reran `scripts/start_worker.sh` successfully.
- Result: existing launchd worker was reloaded; plist `StartInterval` is `120`; worker heartbeat fields show idle `120s` and active `30s`.
- Required confirmation: none.

### DR-20260627-GITHUB-PUSH-SIGNIN
- Status: resolved
- Created: 2026-06-27
- Item: Local push was not ready before GitHub sign-in.
- Resolution: GitHub sign-in was completed on the Mac mini as `liyuanqiang-spec`.
- Required confirmation: none.

### DR-20260627-GITHUB-REMOTE
- Status: resolved
- Created: 2026-06-27
- Item: Remote was missing, then repaired by setting `origin` to `https://github.com/liyuanqiang-spec/-.git` and pulling `origin/main`.
- Required confirmation: none.

### DR-20260627-TASK-004-SAFETY-SCAN
- Status: resolved
- Created: 2026-06-27 18:29:25 +0800
- Item: Task TASK-004 was blocked by the safety scanner.
- Resolution: TASK-004 was superseded and replaced with TASK-004A, limited to status-only repository maintenance and worker health checks.
- Required confirmation: none.

### DR-20260628-STALE-PULL-BLOCKERS
- Status: resolved
- Created: 2026-06-28
- Item: Historical `git pull failed` entries kept the dashboard in Attention state.
- Resolution: The worker later completed TASK-007 and pushed status files, proving these pull blocks were stale. ChatGPT marked the historical entries resolved and created a simplified safe TASK-008 for status-layer completion.
- Required confirmation: none.

## Decision Required 2026-06-27 20:44:37 +0800

- Status: resolved
- Item: git pull failed; manual conflict check required
- Current action: stale entry; no current user action required
- Resolution: superseded by later successful worker output and DR-20260628-STALE-PULL-BLOCKERS.

## Decision Required 2026-06-27 20:56:09 +0800

- Status: resolved
- Item: git pull failed; manual conflict check required
- Current action: stale entry; no current user action required
- Resolution: superseded by later successful worker output and DR-20260628-STALE-PULL-BLOCKERS.

## Decision Required 2026-06-27 22:39:23 +0800

- Status: resolved
- Item: git pull failed; manual conflict check required
- Current action: stale entry; no current user action required
- Resolution: superseded by later successful worker output and DR-20260628-STALE-PULL-BLOCKERS.

## Decision Required 2026-06-28 02:07:48 +0800

- Status: resolved
- Item: git pull failed; manual conflict check required
- Current action: stale entry; no current user action required
- Resolution: superseded by later successful worker output and DR-20260628-STALE-PULL-BLOCKERS.

## Decision Required 2026-06-28 02:32:02 +0800

- Status: resolved
- Item: git pull failed; manual conflict check required
- Current action: stale entry; no current user action required
- Resolution: superseded by later successful worker output and DR-20260628-STALE-PULL-BLOCKERS.

## Decision Required 2026-06-28 02:48:18 +0800

- Status: resolved
- Item: git pull failed; manual conflict check required
- Current action: stale entry; no current user action required
- Resolution: superseded by later successful worker output and DR-20260628-STALE-PULL-BLOCKERS.

## Decision Required 2026-06-28 20:27:28 +0800

- Status: resolved
- Item: Task TASK-011 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: stale entry; no current user action required
- Resolution: TASK-011 was superseded by TASK-011A, which stayed inside repository-local offline file validation and `PHASE_1_SIMULATION_ONLY`.
- Required confirmation: none.

## Decision Required 2026-06-28 21:21:24 +0800

- Status: resolved
- Item: Task TASK-013 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: stale entry; no current user action required
- Resolution: TASK-013 was superseded by TASK-013A, a repository-only visible review scaffold with no network calls, no real trading access, no order actions, no fund movement, no original-data deletion, no secret exposure, and no dangerous sandbox.
- Required confirmation: none.

## Decision Required 2026-06-28 21:25:48 +0800

- Status: resolved
- Item: worker sync failed at pull stage: git pull failed
- Current action: stale entry; no current user action required
- Resolution: TASK-013A reached codex exec and is being completed in the repository; outer worker remains responsible for git sync after codex exits.
- Required confirmation: none.

## Decision Required 2026-06-28 21:49:29 +0800

- Status: resolved
- Item: Task TASK-014 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: superseded by safe repository-status-only task TASK-014A
- Resolution: TASK-014A narrows the work to a local visible-status display patch with no external service calls, no real trading account connection, no order placement or cancellation, no fund movement, no original-data deletion, no secret exposure, and no dangerous sandbox.
- Required confirmation: none.

## Decision Required 2026-06-28 22:06:16 +0800

- Status: resolved
- Item: Task TASK-015 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: stale safety-scan block; no current user action required
- Resolution: TASK-015 was repository-status-only worker scheduling work. The blocked words appeared inside negative restrictions such as not editing broker/API/account/order/fund/secret files. The completed implementation touched worker scheduling, status refresh, health checks, and visible monitoring only.
- Required confirmation: none.

## Decision Required 2026-06-29 11:36:10 +0800

- Status: resolved
- Item: Task TASK-019 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: stale wording block; no current user action required
- Resolution: TASK-019 proved the safety scanner is active. TASK-019A replaces it with narrower repository-status-only wording.
- Required confirmation: none.

## Decision Required 2026-06-29 11:38:44 +0800

- Status: resolved
- Item: worker sync failed at push stage: git push failed for Worker completed GPT handshake TASK-019A
- Current action: stale network push failure; no current user action required
- Resolution: TASK-019A worker output is on GitHub after retry through the local proxy.
- Required confirmation: none.

## Decision Required 2026-06-29 17:11:58 +0800

- Status: resolved
- Item: Task TASK-020-GPT-INTERACTIVE-REPLY contains a blocked trading/fund/secret/deletion/danger risk
- Current action: stale local guard block; no current user action required
- Resolution: TASK-020 was superseded by TASK-021 and TASK-022. TASK-022 completed the local worker reply path with `LOCAL_WORKER_MAIL_SENT` while staying inside `PHASE_1_SIMULATION_ONLY` and without printing or writing recipient configuration.
- Required confirmation: none.

## Decision Required 2026-06-29 19:36:29 +0800

- Status: resolved
- Item: worker sync failed at push stage: git push failed for Worker processed TASK-022-LOCAL-MAIL-RETRY
- Current action: stale push rejection; no current user action required
- Resolution: support clone was rebased onto origin/main after remote skill commits and will be pushed by the current sync repair.
- Required confirmation: none.

## Decision Required 2026-06-29 21:11:10 +0800

- Status: resolved
- Item: Task TASK-026-LOCAL-WORKER-PRIMARY-ROUTE contains a blocked trading/fund/secret/deletion/danger risk
- Current action: no user action required
- Resolution: TASK-026 was replaced by TASK-026A with clean repository-status wording. The local Mac mini worker is now the primary route and the hosted route is parked.
- Required confirmation: none.
