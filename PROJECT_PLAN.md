# PROJECT_PLAN.md

## Goal

Build an unattended GitHub-supervised silver options/futures quantitative research system.

## Phase 1: Safe Research MVP

- Maintain GitHub status files
- Run local Codex worker on Mac mini
- Define data schema
- Build option contract scanner
- Build spread calculator
- Build simple backtest
- Build report writer
- Enforce risk controls

## Phase 2: Data Foundation

- Add read-only market data sources
- Validate option daily, tick, quote, trade, position, margin, and fee fields
- Keep original data append-only
- Produce data quality reports

## Phase 3: Research Automation

- Scan inactive but open-interest contracts
- Rank low-liquidity candidates
- Estimate spread width and passive-fill opportunity
- Generate Chinese summary reports

## Phase 4: Simulation

- Add simulated order records
- Add missing-leg and timeout gates
- Add kill switches
- Keep real trading blocked

## Non-Goals

- No real broker connection
- No real order placement
- No real order cancellation
- No fund transfer
- No deletion of original data
- No secret exposure
