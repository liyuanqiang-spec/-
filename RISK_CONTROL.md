# RISK_CONTROL.md

## Current Permission Level

`SIMULATION_ONLY`

## Allowed

- Data download
- Data cleaning
- Option contract scanning
- Spread calculation
- Backtesting
- Simulated trading preparation
- Report generation

## Hard Stops

The agent must stop and wait for explicit user confirmation before:

1. Real order placement
2. Real broker execution
3. Real order cancellation
4. Broker login automation that can trade
5. Broker-side permission changes
6. Fund transfer
7. Margin movement
8. Deleting original/raw market data
9. Publishing sensitive trading data
10. Secret exposure or unsafe key handling
11. `danger-full-access` escalation for a task
12. System-level modification
13. Large paid API or cloud calls
14. Switching simulation to production

## Default Kill Switches

| Risk | Default Control |
|---|---|
| Missing market data | Stop scan/backtest |
| Stale quote | Exclude candidate |
| Bid-ask too wide | Exclude or mark high risk |
| Incomplete spread legs | Stop simulated submission |
| Leg fill timeout | Stop after 3 seconds in simulation design |
| Excessive drawdown | Stop strategy and report |
| Unknown account mode | Treat as no-trade |
| Unknown task safety | Write `DECISION_REQUIRED.md` and stop |
| Unsupported worker task | Write `DECISION_REQUIRED.md` and stop |

## Decision Rule

If a decision is required, provide exactly A/B/C options and recommend one.

## Current Trading State

No real trading is authorized in this project.

## Worker Permission Level

The background worker can only run:

- `pipeline`
- `report`
- `test`
- `status_check`

All other task types require Codex review or user confirmation before execution.
