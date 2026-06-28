# Codex Quant Minimal Report

结论：当前系统处于 `SIMULATION_ONLY`，本报告只基于样例数据，不代表真实交易建议。

## Summary

- Contracts after scan: 7
- Spread candidates: 4
- Backtest reliability: LOW_SAMPLE
- Estimated edge: 18.0
- Max loss per spread: 40.0

## Top Candidates

| Long | Short | Type | Expiry | Strikes | Net Debit | Liquidity Score |
|---|---|---:|---|---:|---:|---:|
| AG2608C7200 | AG2608C7400 | C | 2026-08-15 | 7200-7400 | 40 | 1664.73 |
| AG2608P7200 | AG2608P7000 | P | 2026-08-15 | 7000-7200 | 20 | 672.28 |
| AG2608C7400 | AG2608C7600 | C | 2026-08-15 | 7400-7600 | 26 | 636 |
| AG2609C7200 | AG2609C7400 | C | 2026-09-15 | 7200-7400 | 46 | 366.28 |

## Risk Issues

- LOW_SAMPLE: candidate count is below 20
- REJECTED_CANDIDATES: 1 candidate(s) failed simulation gates
- LOW_TRADE_COUNT: fewer than 5 simulated accepted spreads

## Safety

- Real trading: blocked
- Broker orders: blocked
- Fund transfer: blocked
