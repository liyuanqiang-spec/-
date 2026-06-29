# Cloud automation setup

This repository now has a cloud-first automation path that does not require the Mac mini for repository supervision.

## Installed workflows

1. `.github/workflows/gpt-supervisor.yml`
   - Runs hourly and manually.
   - Reads repository ledger/status files.
   - Calls the OpenAI Responses API when `OPENAI_API_KEY` exists.
   - Writes `GPT_REVIEW.md`, `GPT_VISIBLE_STATUS.md`, and `.gpt_state.json`.
   - Appends at most one safe repository-only task when the queue is idle.

2. `.github/workflows/codex-task-runner.yml`
   - Runs hourly and manually.
   - Checks whether `TASK_QUEUE.md` has a pending task.
   - Calls `openai/codex-action@v1` only when `OPENAI_API_KEY` exists and a pending task exists.
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
2. Manually run `GPT Supervisor` once.
3. Check `GPT_REVIEW.md` and `GPT_VISIBLE_STATUS.md`.
4. Manually run `Codex Task Runner` once if `TASK_QUEUE.md` has a safe pending task.
5. After the first manual run is clean, rely on hourly schedule.

If the Mac mini worker is also running, pause it before relying on the cloud runner to avoid duplicate workers acting on the same pending task.
