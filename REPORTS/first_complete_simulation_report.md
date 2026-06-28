# TASK-007 First Complete Simulation Report

结论：第一版完整模拟链路已跑通。它只读取本地样例白银期权数据，生成垂直价差候选，估算被动第一腿成交机会，模拟第二腿补腿滑点，执行风控检查，并写出本报告。全程未连接真实交易账户，未下单，未撤单，未转账。

## Run Command

```bash
python3 -m src.codex_quant.run_pipeline --first-complete-simulation
```

## Dashboard Entry

| Metric | Value |
|---|---:|
| Contracts scanned | 7 |
| Vertical spread candidates | 4 |
| Rejected candidates | 1 |
| Accepted simulated spreads | 3 |
| Average simulated edge | 2.398 |
| Worst simulated slippage | 3.2571 |
| Trade count | 3 |
| Win rate | 100.00% |
| Max drawdown | 0 |
| Reliability | LOW_SAMPLE |
| Risk flags | LOW_PASSIVE_FILL, LOW_SAMPLE, WIDE_LEG_SPREAD |

## Reproducible Backtest Configuration

- Contract universe: `8` local sample silver option contracts from `data/contracts/sample_options.csv`.
- Entry rule: build adjacent-strike vertical spreads by underlying, expiry, and option type; first leg is selected as the less liquid leg and quoted passively inside the spread.
- Second-leg rule: once the passive first leg is assumed filled, hedge the other leg immediately with deterministic slippage based on spread width and volume.
- Exit rule: no live exit order is simulated; this first version evaluates entry quality and maximum entry risk only.
- Fee assumption: `0.2` option points per leg.
- Slippage assumption: second-leg slippage is a deterministic function of bid-ask spread, spread percentage, and low-volume penalty.
- Data source: local sample CSV only; no market connection, account query, broker API, credentials, or external paid API call.

## Candidate Simulation Table

| Rank | Long | Short | Type | Expiry | Strikes | Net Debit | First Leg | Passive Fill Prob | Passive Edge | Hedge Leg | Hedge Slippage | Sim Edge | Accepted | Risk Flags |
|---:|---|---|---:|---|---:|---:|---|---:|---:|---|---:|---:|---:|---|
| 1 | AG2608C7200 | AG2608C7400 | C | 2026-08-15 | 7200-7400 | 40 | SELL AG2608C7400 @ 49 | 78.94% | 1 | BUY AG2608C7200 | 0.7524 | 2.2476 | yes | None |
| 2 | AG2608P7200 | AG2608P7000 | P | 2026-08-15 | 7000-7200 | 20 | SELL AG2608P7000 @ 23 | 61.18% | 1 | BUY AG2608P7200 | 0.9368 | 2.0632 | yes | WIDE_LEG_SPREAD |
| 3 | AG2608C7400 | AG2608C7600 | C | 2026-08-15 | 7400-7600 | 26 | SELL AG2608C7600 @ 27.75 | 51.11% | 1.25 | BUY AG2608C7400 | 0.8667 | 2.8833 | yes | WIDE_LEG_SPREAD |
| 4 | AG2609C7200 | AG2609C7400 | C | 2026-09-15 | 7200-7400 | 46 | SELL AG2609C7400 @ 77.5 | 34.62% | 2.5 | BUY AG2609C7200 | 3.2571 | 4.2429 | no | LOW_PASSIVE_FILL |

## Accepted Candidates

- AG2608C7200/AG2608C7400: simulated edge 2.2476, fill probability 78.94%.
- AG2608P7200/AG2608P7000: simulated edge 2.0632, fill probability 61.18%.
- AG2608C7400/AG2608C7600: simulated edge 2.8833, fill probability 51.11%.

## Rejected Candidates

- AG2609C7200/AG2609C7400: LOW_PASSIVE_FILL.

## Contract Scan Rejections

| Symbol | Volume | Open Interest | Spread % | Reason |
|---|---:|---:|---:|---|
| AG2608P6800 | 60 | 420 | 30.77% | spread percentage above maximum |

## Risk Checks

- LOW_SAMPLE: candidate count is below 20
- REJECTED_CANDIDATES: 1 candidate(s) failed simulation gates
- LOW_TRADE_COUNT: fewer than 5 simulated accepted spreads

## Safety Boundary

- Phase: `PHASE_1_SIMULATION_ONLY`.
- Real trading account connection: blocked and not used.
- Real order placement/cancellation: blocked and not used.
- Fund transfer: blocked and not used.
- Original/raw data deletion: blocked and not used.
- Secrets, passwords, tokens, and API keys: not read or exposed.
- `danger-full-access`: not used.
