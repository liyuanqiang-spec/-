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

### DR-20260627-GITHUB-PUSH-AUTH
- Status: waiting_user
- Created: 2026-06-27
- Item: Local `git push origin main` failed with `fatal: could not read Username for 'https://github.com': Device not configured`.
- Required confirmation: authorize GitHub on this Mac mini so unattended `git push` can work.
- A 推荐: run `gh auth login` or configure a GitHub credential/token for repository `liyuanqiang-spec/-`, then rerun the push.
- B: provide an SSH remote and install an SSH key with write permission.
- C: keep local-only mode and do not use GitHub supervision.

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
