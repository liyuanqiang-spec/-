---
name: liquidity-spread
description: Use for scanning option liquidity, bid-ask spreads, passive-fill candidates, vertical spreads, and cross-strike relative value.
---

# Liquidity Spread Skill

Use this skill for liquidity-aware option spread research.

## Rules

1. Prefer full-chain scans over one fixed strike.
2. Track bid, ask, mid, spread width, volume, open interest, and quote freshness.
3. Mark candidates as research or simulation only.
4. Highlight leg risk and incomplete-fill risk.
5. Any execution discussion must stay in simulated mode unless the user explicitly confirms otherwise.

## Output

- Candidate spreads
- Liquidity score
- Leg-risk notes
- Simulation readiness
