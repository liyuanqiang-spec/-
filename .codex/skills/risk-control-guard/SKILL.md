---
name: risk-control-guard
description: Use before executing any task that may touch external systems, local software, data files, or automation controls.
---

# risk-control-guard

## Purpose

Keep project work safe, reversible, and simulation-only unless the user gives a separate explicit instruction.

## Hard boundaries

- Keep `PHASE_1_SIMULATION_ONLY` for quant work.
- Do not touch live accounts or production trading paths.
- Do not delete original data.
- Do not expose private configuration.
- Do not use dangerous escalation.

## If a task is unsafe

- Stop before execution.
- Mark the task `decision_required`.
- Write a concise blocker reason.
- Prefer rewriting into a narrower safe task.
