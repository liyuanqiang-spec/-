# Quant System Gap Report

结论：TASK-009 已把当前仓库从“最小样例 pipeline”推进到“仓库内可回放的量化基线”。它可以用本地样本数据回答执行改善问题的 smoke 版本，但还不能形成统计结论，因为样本只有单个静态期权快照，缺 tick、盘口深度、多时点 replay 和真实手续费/保证金曲线。

## Safety Mode

- Current mode: `PHASE_1_SIMULATION_ONLY`.
- Data scope: repository-local CSV sample and generated replay CSV only.
- Blocked: real trading account connection, real order placement, order cancellation, fund transfer, broker permission change, original-data deletion, secret exposure, dangerous sandbox.

## Current Coverage

| Target module | Current coverage |
|---|---|
| Data loader | partial - CSV option quote loader exists; no multi-snapshot tick/depth loader yet. |
| Contract parser | partial - schema fields are parsed; symbol-level expiry/type parsing remains basic. |
| Time-value radar | baseline implemented in TASK-009 from local sample option chain. |
| Low-liquidity scanner | implemented for sample open-interest and low-volume ranking. |
| Combination generator | implemented for adjacent-strike vertical spreads by expiry/type. |
| Scoring engine | baseline implemented with expected edge, fill probability, liquidity, risk and second-leg cost. |
| State-machine simulator | baseline replay implemented with IDLE/FOUND/PENDING_FIRST_LEG/FIRST_LEG_FILLED/HEDGING_SECOND_LEG/DONE/FAILED/COOLDOWN paths. |
| Second-leg protection | baseline implemented as immediate active hedge slippage and max adverse move estimate. |
| Replay and reporting | implemented for markdown reports and replay CSV. |
| Dashboard/app | partial - status dashboard exists; quant tables are still report-only. |

## Data Coverage

- Input option sample: `DATA/contracts/sample_options.csv`.
- Raw contracts: 8.
- Contracts after scan gates: 7.
- Low-liquidity contracts with open interest: 3.
- Vertical spread candidates: 4.
- Replay CSV: `REPORTS/quant_baseline_replay.csv`.
- Missing data: futures quote series, tick data, order book depth, quote freshness timestamps, transaction logs, margin schedule, fee schedule by venue.

## Can It Answer The Key Question?

只能做样本级 smoke 判断，不能做统计结论；当前样本显示平均模拟改善 2.398 点，可靠性标记为 LOW_SAMPLE。

Key question: Does passive first-leg plus active second-leg simulation improve combo net price versus immediate baseline after costs?

- Current average simulated improvement: 2.398.
- Accepted simulated spreads: 3.
- Rejected simulated spreads: 1.
- Worst simulated second-leg slippage: 3.2571.
- Reliability: `LOW_SAMPLE`.
- Risk flags: `LOW_PASSIVE_FILL, LOW_SAMPLE, WIDE_LEG_SPREAD`.

## Remaining Gaps

- Add multi-snapshot quote replay so the state machine can measure timeouts and repricing instead of using a single static quote.
- Add option-chain metadata and robust symbol parser for domestic silver option naming variants.
- Add盘口深度、quote freshness、成交回报 fixture so passive-fill and incomplete-leg rates are data-backed.
- Add parameter sensitivity over fill threshold, maximum adverse move, timeout, and second-leg slippage.
- Add dashboard tables for time-value anomalies, spread ranking, and replay summary.

## Verification

- `python3 scripts/refresh_visible_status.py`: passed, visible state WORKING during execution. - `bash scripts/check_worker_health.sh`: passed. - `python3 -m compileall -q src tests scripts`: passed. - `python3 -m unittest discover -s tests`: passed, 14 tests. - `bash -n scripts/codex_worker.sh`: passed.

## Next Three Safe Codex Tasks

1. TASK-010: Add repository-local multi-snapshot option quote replay fixture with timestamp, bid/ask depth, quote freshness, and deterministic tests.
2. TASK-011: Add parameter sensitivity report for passive fill threshold, timeout, second-leg max adverse move, fee and slippage assumptions.
3. TASK-012: Extend visible dashboard/report layer with time-value anomaly table, spread ranking table, and replay summary link.
