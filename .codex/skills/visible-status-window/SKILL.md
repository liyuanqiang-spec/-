---
name: visible-status-window
description: Use when the user wants a simple status view instead of technical logs.
---

# visible-status-window

## Purpose

Convert worker state into a simple user-facing window.

## Output format

Use short rows such as:

| Side | Status |
|---|---|
| GPT | DONE |
| Local worker | RUNNING |
| External check | SENT |
| Overall | PARTIAL_SUCCESS |

## Status vocabulary

- `DONE`
- `RUNNING`
- `BLOCKED`
- `FAILED`
- `SENT`
- `SKIPPED`
- `PARTIAL_SUCCESS`
- `SUCCESS`

## Rules

- Keep details out of the user-facing window.
- Put technical details in `RUN_LOG.md` only.
- Do not expose local configuration.
