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
- Status: waiting_user
- Created: 2026-06-27
- Item: Requested GitHub repository is `liyuanqiang-spec/-`, but `git remote -v` returned no remote in this local project. Per user rule, execution stopped before pull, file regeneration, worker changes, email test, push, or PR work.
- Required confirmation: connect this local folder to `liyuanqiang-spec/-` or provide the correct repository/remote URL.
- A 推荐: add remote `origin` pointing to `liyuanqiang-spec/-`, then rerun the initialization and push workflow.
- B: choose a different GitHub repository and update this decision.
- C: keep local-only mode and skip GitHub supervision.

### DR-0001
- Status: waiting_user
- Created: 2026-06-27
- Item: Local Git has been initialized, but GitHub remote and PR automation are not active because no remote/authenticated GitHub target is configured.
- A 推荐: keep local commits now, connect a GitHub remote later when you want PRs.
- B: authorize GitHub CLI/browser login and provide or create the target remote.
- C: skip Git/PR automation and use status files only.
