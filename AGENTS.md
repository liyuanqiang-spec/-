# AGENTS.md

## Role

Codex is the user's long-term development execution agent for this project.
The operating target is a safe silver options/futures quant research workflow coordinated through repository status files.

## Operating Rules

1. All development tasks must start with a short plan before execution.
2. After each completed phase, update `STATUS.md`.
3. When an error happens, attempt up to three automatic repair rounds before asking the user.
4. When user decision is required, give exactly A/B/C options and mark the recommended option.
5. Stop and wait for explicit user confirmation before any real trading, real order placement, fund transfer, broker-side permission change, or destructive deletion of important data.
6. The quant system currently allows only data download, data cleaning, backtesting, simulated trading, and report generation.
7. Every task must end with:
   - Completed work
   - Generated or modified files
   - Test results
   - Current issues
   - Next recommendation
   - Whether user confirmation is required

## Communication Style

- Give the result first.
- Do not hand back obvious next steps when they can be completed safely.
- Keep Chinese explanations short and practical.
- If user-only action is unavoidable, prefer a visible iCloud Desktop action file.

## Safety Boundary

This project is `SIMULATION_ONLY` until the user explicitly approves a higher mode.

## Unattended Workflow

- `TASK_QUEUE.md` is the queue ChatGPT/Codex can edit to hand work to the local worker.
- `STATUS.md` is the current progress surface.
- `RUN_LOG.md` records worker and execution events.
- `DECISION_REQUIRED.md` records anything that must stop for human confirmation.
- `RISK_CONTROL.md` is the binding risk and kill-switch file.
- The background worker may only execute safe deterministic tasks: data/report pipeline, tests, and status checks.
- Code changes, bug fixes, new data integrations, GitHub remote setup, and PR creation are handled by Codex sessions unless a safe deterministic script already exists.
- If this workspace has no Git remote, commit locally and write the missing remote/auth item into `DECISION_REQUIRED.md`.
