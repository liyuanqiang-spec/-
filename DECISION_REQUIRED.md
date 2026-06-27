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
