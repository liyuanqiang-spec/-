# DECISION_REQUIRED.md

Current mode: `SIMULATION_ONLY`

For binding safety limits, see `RISK_CONTROL.md`.

## Open Decisions

No current user action required for normal safe GitHub status-file supervision.

## Resolved Decisions

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
