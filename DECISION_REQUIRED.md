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
- Status: waiting_user
- Created: 2026-06-27
- Item: Local Git has been initialized, but GitHub remote and PR automation are not active because no remote/authenticated GitHub target is configured.
- A 推荐: keep local commits now, connect a GitHub remote later when you want PRs.
- B: authorize GitHub CLI/browser login and provide or create the target remote.
- C: skip Git/PR automation and use status files only.

## Decision Required 2026-06-27 16:45:37 +0800

- Item: Task TASK-001 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: worker stopped before execution
- A 推荐: keep simulation-only and rewrite the task as safe research work
- B: explicitly authorize the blocked setup/action
- C: cancel this task
