# Start Here: One Click Cloud Automation

This is the simplest path for the owner.

## What is already installed

The repository already includes these workflows:

1. `One Click Setup`
   - Refreshes `CLOUD_AUTOMATION_DASHBOARD.md`.
   - Checks only whether `OPENAI_API_KEY` exists.
   - Runs `scripts/gpt_supervisor.py` only when the key exists.

2. `GPT Supervisor`
   - Reads repository status files.
   - Calls OpenAI when `OPENAI_API_KEY` exists.
   - Writes `GPT_REVIEW.md`, `GPT_VISIBLE_STATUS.md`, and `.gpt_state.json`.

3. `Codex Task Runner`
   - Runs `openai/codex-action@v1` when `OPENAI_API_KEY` exists and a safe repository task exists.

## Owner-only step

Add one GitHub repository secret:

```text
OPENAI_API_KEY
```

Path:

```text
GitHub repository -> Settings -> Secrets and variables -> Actions -> New repository secret
```

Do not put the key in any repository file or issue.

## One-click run

After the secret is added:

```text
GitHub repository -> Actions -> One Click Setup -> Run workflow -> main -> Run workflow
```

Then open:

```text
CLOUD_AUTOMATION_DASHBOARD.md
```

## Status meanings

| Status | Meaning |
|---|---|
| `installed_blocked_by_missing_key` | Workflow exists, but the owner still needs to add `OPENAI_API_KEY` as a GitHub Actions secret. |
| `verified_ready_for_openai` | Key is present and the cloud supervisor can run. |
| `CLOUD_AUTOMATION_DASHBOARD.md` exists | GitHub Actions can write visible setup status back into the repository. |

## Safety boundary

Current mode remains:

```text
PHASE_1_SIMULATION_ONLY
```

Hard stops remain:

- no real trading accounts,
- no orders or cancellations,
- no fund movement,
- no credential exposure,
- no raw/original data deletion,
- no dangerous permissions.
