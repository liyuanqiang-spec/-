---
name: market-data-loader
description: Use when loading, validating, and summarizing local market data files for simulation.
---

# market-data-loader

## Purpose

Find, load, validate, and summarize local market data used by the simulation pipeline.

## Inputs

- CSV fixtures.
- Quote replay files.
- Tick replay files.
- Daily screening files.

## Checks

- Required columns exist.
- Datetime ordering is stable.
- Bid/ask fields are valid when present.
- Missing rows are reported, not hidden.
- No raw source file is deleted.

## Output

Write a compact validation report under `REPORTS/` and update visible status when useful.
