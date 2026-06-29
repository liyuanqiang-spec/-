---
name: quant-backtest
description: Use when building or checking simulation-only quant backtests for futures, options, spreads, and replay data.
---

# quant-backtest

## Purpose

Build, run, and review simulation-only strategy tests.

## Scope

- Daily data screening.
- Quote or tick replay.
- Passive first-leg fill assumptions.
- Active second-leg hedge assumptions.
- Fees, slippage, timeout, and incomplete-leg handling.
- Deterministic reports and tests.

## Rules

- Keep `PHASE_1_SIMULATION_ONLY`.
- Do not connect to live trading software.
- Do not place, cancel, or simulate real orders outside local fixtures.
- Make results reproducible.
- Write reports under `REPORTS/`.
