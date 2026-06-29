# Cloud automation setup

This repository now has a cloud-first automation path that does not require the Mac mini for repository supervision.

## Simplest start

Use this file first:

```text
START_HERE_ONE_CLICK.md
```

Then run this workflow from GitHub Actions:

```text
One Click Setup
```

The workflow writes or refreshes:

```text
CLOUD_AUTOMATION_DASHBOARD.md
ONE_CLICK_STATUS.md
```

## Installed workflows

1. `.github/workflows/one-click-setup.yml`
   - Runs manually.
   - Refreshes `CLOUD_AUTOMATION_DASHBOARD.md`.
   - Checks only whether `OPENAI_API_KEY` exists.
   - Runs the GPT supervisor only when the key exists.

2. `.github/workflows/gpt-supervisor.yml`
   - Runs hourly and manually.
   - Reads repository ledger/status files.
   - Calls the OpenAI Responses API when `OPENAI_API_KEY` exists.
   - Writes `GPT_REVIEW.md`, `GPT_VISIBLE_STATUS.md`, and `.gpt_state.json`.
   - Appends at most one safe repository-only task when the queue is idle.

3. `.github/workflows/codex-task-runner.yml`
   - Runs hourly and manually.
   - Checks whether `TASK_QUEUE.md` has a pending task.
   - Calls `openai/codex-action@v1` only when `OPENAI_API_KEY` exists and a pending task or safe owner issue task exists.
   - Commits Codex changes back to the repository.

## Required GitHub secret

Add one repository secret:

```text
OPENAI_API_KEY
```

Do not put the key in any repository file.

## Optional repository variable

You may add this repository variable if the default model is unavailable for your OpenAI account:

```text
OPENAI_MODEL
```

If omitted, `scripts/gpt_supervisor.py` uses `gpt-5.5`.

## Safety boundary

Current mode remains:

```text
PHASE_1_SIMULATION_ONLY
```

Hard stops remain:

- no real trading accounts,
- no orders or cancellations,
- no fund movement,
- no secret exposure,
- no raw/original data deletion,
- no dangerous permissions.

## Recommended activation order

1. Add `OPENAI_API_KEY` as a GitHub Actions repository secret.
2. Manually run `One Click Setup` once.
3. Check `CLOUD_AUTOMATION_DASHBOARD.md`.
4. Run `Codex Task Runner` only when there is a safe pending task or a safe owner-created issue task.
5. After the first manual run is clean, rely on hourly schedule for `GPT Supervisor` and `Codex Task Runner`.

If the Mac mini worker is also running, pause it before relying on the cloud runner to avoid duplicate workers acting on the same pending task.
