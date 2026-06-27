---
name: options-backtest
description: Use for designing and running options backtests with contract filtering, spread construction, risk constraints, and result summaries.
---

# Options Backtest Skill

Use this skill when testing options strategies.

## Rules

1. Backtests must be reproducible.
2. State contract universe, entry rule, exit rule, fees, slippage, and margin assumptions.
3. Treat low liquidity, missing quotes, and wide bid-ask spreads as first-class risks.
4. Backtest output must include drawdown, trade count, win rate, and sample-size warning.
5. No real orders or broker submission code.

## Output

- Backtest configuration
- Result table
- Risk summary
- Reliability score
