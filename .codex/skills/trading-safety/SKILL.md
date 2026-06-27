---
name: trading-safety
description: Use for enforcing the project's hard boundary: data, cleaning, backtesting, simulation, and reports are allowed; real trading is blocked.
---

# Trading Safety Skill

Use this skill whenever code, data, or automation touches trading workflows.

## Hard Boundary

Allowed:

- Data download
- Data cleaning
- Contract scanning
- Backtesting
- Simulated trading
- Report generation

Blocked without explicit user confirmation:

- Real order placement
- Broker login automation that can trade
- Fund transfer
- Margin movement
- Destructive deletion of important data
- Turning simulation into production execution

## Output

- Current mode
- Blocked actions
- Required user confirmation
