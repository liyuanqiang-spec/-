---
name: risk-control
description: Use for position sizing, kill switches, drawdown controls, missing-data gates, and project risk documentation.
---

# Risk Control Skill

Use this skill before any strategy is marked ready for simulation.

## Rules

1. Real trading is blocked by default.
2. Enforce data completeness checks before backtest or simulation.
3. Enforce kill switches for missing legs, stale quotes, wide spreads, drawdown, and abnormal order counts.
4. Write all critical controls into `RISK_CONTROL.md`.
5. Stop and ask for confirmation before real trading, fund movement, or destructive data deletion.

## Output

- Risk gates
- Kill switches
- Current permission level
- Required confirmation
