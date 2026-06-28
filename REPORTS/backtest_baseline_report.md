# Backtest Baseline Report

结论：本次回测基线已跑通“期权链扫描 -> 时间价值雷达 -> 垂直价差生成 -> 评分 -> 第一腿被动成交模拟 -> 第二腿主动补腿模拟 -> replay 报告”。当前结果只适合作为 pipeline 验证，不代表真实收益能力。

## Reproducible Configuration

- Contract universe: `DATA/contracts/sample_options.csv`.
- Scan gate: `volume >= 30`, `spread_pct <= 25%`.
- Entry rule: adjacent-strike vertical spreads by underlying, expiry, and option type.
- First-leg rule: less liquid leg is quoted passively inside its bid-ask spread.
- Second-leg rule: after simulated first-leg fill, the other leg is completed immediately with deterministic active hedge slippage.
- Exit rule: no live exit; this baseline evaluates entry quality and leg-completion risk only.
- Fee assumption: 0.2 option points per leg.
- Margin/risk assumption: max loss is capped by vertical width for acceptable debit spreads; candidates breaching width are rejected.
- Data source: local fixture/sample only; no broker, account, market feed, paid API, or credential access.

## Result Table

| Metric | Value |
|---|---:|
| Raw contracts | 8 |
| Contracts after scan | 7 |
| Vertical spread candidates | 4 |
| Accepted simulated spreads | 3 |
| Rejected simulated spreads | 1 |
| Trade count | 3 |
| Win rate | 100.00% |
| Average net improvement | 2.398 |
| Worst simulated second-leg slippage | 3.2571 |
| Max drawdown | 0 |
| Incomplete-leg rate | 25.00% |
| Reliability | LOW_SAMPLE |

## Top Scored Spreads

| Rank | Long | Short | Type | Expiry | Strikes | Fill Prob | Sim Edge | Expected Edge | Second-leg Cost | Max Adverse Move | Score | State Path | Flags |
|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | AG2608C7200 | AG2608C7400 | C | 2026-08-15 | 7200-7400 | 78.94% | 2.2476 | 0.8219 | 0.9524 | 0.7524 | 20.6543 | IDLE > FOUND > PENDING_FIRST_LEG > FIRST_LEG_FILLED > HEDGING_SECOND_LEG > DONE | None |
| 2 | AG2608C7400 | AG2608C7600 | C | 2026-08-15 | 7400-7600 | 51.11% | 2.8833 | 0.407 | 1.0667 | 0.8667 | -11.848 | IDLE > FOUND > PENDING_FIRST_LEG > FIRST_LEG_FILLED > HEDGING_SECOND_LEG > DONE | WIDE_LEG_SPREAD |
| 3 | AG2608P7200 | AG2608P7000 | P | 2026-08-15 | 7000-7200 | 61.18% | 2.0632 | 0.1255 | 1.1368 | 0.9368 | -12.2862 | IDLE > FOUND > PENDING_FIRST_LEG > FIRST_LEG_FILLED > HEDGING_SECOND_LEG > DONE | WIDE_LEG_SPREAD |
| 4 | AG2609C7200 | AG2609C7400 | C | 2026-09-15 | 7200-7400 | 34.62% | 4.2429 | -1.9882 | 3.4571 | 3.2571 | -53.0807 | IDLE > FOUND > PENDING_FIRST_LEG > FAILED > COOLDOWN | LOW_PASSIVE_FILL |

## Time-Value Radar

| Symbol | Type | Expiry | Strike | Inferred Underlying | Intrinsic | Mid Time Value | Spread % | Parity Dev | Flags |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| AG2608C7200 | C | 2026-08-15 | 7200 | 7246 | 46 | 38 | 4.76% | 0 | OK |
| AG2608C7400 | C | 2026-08-15 | 7400 | 7246 | 0 | 48 | 8.33% |  | OK |
| AG2608C7600 | C | 2026-08-15 | 7600 | 7246 | 0 | 26.5 | 18.87% |  | WIDE_SPREAD |
| AG2608P6800 | P | 2026-08-15 | 6800 | 7246 | 0 | 13 | 30.77% |  | WIDE_SPREAD |
| AG2608P7000 | P | 2026-08-15 | 7000 | 7246 | 0 | 22 | 18.18% |  | WIDE_SPREAD |
| AG2608P7200 | P | 2026-08-15 | 7200 | 7246 | 0 | 38 | 10.53% | 0 | OK |
| AG2609C7200 | C | 2026-09-15 | 7200 | 7300 | 100 | 12 | 7.14% |  | OK |
| AG2609C7400 | C | 2026-09-15 | 7400 | 7300 | 0 | 75 | 13.33% |  | OK |

## Replay Summary

- Replay CSV: `REPORTS/quant_baseline_replay.csv`.
- State paths used: accepted candidates use `IDLE > FOUND > PENDING_FIRST_LEG > FIRST_LEG_FILLED > HEDGING_SECOND_LEG > DONE`; incomplete/rejected candidates use `IDLE > FOUND > PENDING_FIRST_LEG > FAILED > COOLDOWN`.
- Maximum adverse move observed: 3.2571.

## Risk Summary

- LOW_SAMPLE: candidate count is below 20
- REJECTED_CANDIDATES: 1 candidate(s) failed simulation gates
- LOW_TRADE_COUNT: fewer than 5 simulated accepted spreads
- Sample-size warning: `LOW_SAMPLE`.
- Risk flags: `LOW_PASSIVE_FILL, LOW_SAMPLE, WIDE_LEG_SPREAD`.

## Verification

- `python3 scripts/refresh_visible_status.py`: passed, visible state WORKING during execution. - `bash scripts/check_worker_health.sh`: passed. - `python3 -m compileall -q src tests scripts`: passed. - `python3 -m unittest discover -s tests`: passed, 14 tests. - `bash -n scripts/codex_worker.sh`: passed.

## Safety Boundary

- Real trading account connection: blocked and not used.
- Real order placement/cancellation: blocked and not used.
- Fund transfer: blocked and not used.
- Original/raw data deletion: blocked and not used.
- Secrets/API keys/passwords/tokens: not used.
- Dangerous sandbox: not used.
