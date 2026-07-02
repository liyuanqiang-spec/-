# GPT Visible Status

- Generated at: `2026-07-02T15:25:00+08:00`
- Status: `READY`
- Visible scaffold: `SCAFFOLD_READY`
- Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`
- Local review input: `GPT_LOCAL_REVIEW_INPUT.md`
- Worker mode: `WARM`
- Current poll interval: `600s`
- Polling reason: waiting for local worker to pull newest queue
- Night quiet window: `22:00-08:00`
- Safety mode: `PHASE_1_SIMULATION_ONLY`
- Current task: `TASK-032A-IWENCAI-SKILLHUB-PACKAGE` pending
- Latest completed task: TASK-031-ASK-SOFTWARE-ITERATION-STATUS (completed) - Ask Codex for software iteration progress [SOFTWARE_ITERATION_STATUS_20260702] | codex exec completed
- Decision required: no - TASK-032 wording issue superseded by TASK-032A
- Latest status marker: `GPT_CODEX_HANDOFF_SKILL_READY`
- Latest commit: d2668ab 2026-07-02 Supersede blocked Iwencai task with safer wording
- Worker poll interval: active 30s, warm 60s, idle 600s
- Next action: local worker should pull `main` and execute the first safe pending queue item.

## ChatGPT Supervision Contract

- ChatGPT writes safe work into `TASK_QUEUE.md`.
- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.
- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.

## Reusable handoff skill

- Project memory: `PROJECT_MEMORY.md`
- Skill file: `.codex/skills/gpt-codex-github-handoff/SKILL.md`
- Marker: `GPT_CODEX_HANDOFF_SKILL_READY`
