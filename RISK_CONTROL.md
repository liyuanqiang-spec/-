# RISK_CONTROL.md

## Current Permission Level

`PHASE_1_SIMULATION_ONLY`

## Allowed Work

- Data download
- Data cleaning
- Contract scanning
- Spread calculation
- Backtesting
- Simulated trading
- Report generation

## Hard Stops

Codex and the worker must stop before:

1. Connecting to a real trading account
2. Real order placement
3. Real order cancellation
4. Broker-side permission changes
5. Fund transfer
6. Margin movement
7. Deleting original/raw data
8. Secret, password, token, API key exposure
9. `danger-full-access`
10. System-level modification outside this project
11. Large paid API/cloud calls

## Default Risk Gates

| Risk | Control |
|---|---|
| Missing data | Stop scan/backtest and report missing fields |
| Stale quotes | Exclude candidate |
| Wide bid-ask spread | Exclude or mark high risk |
| Missing spread leg | Stop simulated submission |
| Unknown account mode | Treat as no-trade |
| Real trading keyword | Write `DECISION_REQUIRED.md` and stop |
| Secret keyword | Write `DECISION_REQUIRED.md` and stop |
| Raw-data deletion | Write `DECISION_REQUIRED.md` and stop |

## Worker Sandbox

The worker may call Codex only with:

```bash
codex exec --sandbox workspace-write
```

It must never use:

```bash
--sandbox danger-full-access
--dangerously-bypass-approvals-and-sandbox
```
