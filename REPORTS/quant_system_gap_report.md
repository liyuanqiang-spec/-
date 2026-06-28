# Quant System Gap Report

结论：TASK-010 已在 TASK-009 基线上补齐仓库本地多快照报价 replay fixture 和 loader。当前系统可以用本地 fixture 验证有序快照、陈旧报价、第一腿超时、被动成交概率、补腿不利变动、不完整腿和确定性改价/超时行为；但它仍然不能形成真实收益或真实成交统计结论。

## Safety Mode

- Current mode: `PHASE_1_SIMULATION_ONLY`.
- Data scope: repository-local CSV sample and generated replay CSV only.
- Blocked: real trading account connection, real order placement, order cancellation, fund transfer, broker permission change, original-data deletion, secret exposure, dangerous sandbox.

## Current Coverage

| Target module | Current coverage |
|---|---|
| Data loader | implemented for repository fixtures - static option chain loader plus TASK-010 multi-snapshot quote replay loader. |
| Contract parser | partial - schema fields are parsed; symbol-level expiry/type parsing remains basic. |
| Time-value radar | baseline implemented in TASK-009 from local sample option chain. |
| Low-liquidity scanner | implemented for sample open-interest and low-volume ranking. |
| Combination generator | implemented for adjacent-strike vertical spreads by expiry/type. |
| Scoring engine | baseline implemented with expected edge, fill probability, liquidity, risk and second-leg cost. |
| State-machine simulator | implemented for static baseline and TASK-010 ordered multi-snapshot replay with repricing, stale quotes, timeout, fill and incomplete-leg states. |
| Second-leg protection | implemented for fixture replay as adverse-move measurement plus deterministic protection threshold. |
| Replay and reporting | implemented for markdown reports and replay CSV with static and multi-snapshot replay metrics. |
| Dashboard/app | partial - status dashboard exists; quant tables are still report-only. |

## Data Coverage

- Input option sample: `DATA/contracts/sample_options.csv`.
- Raw contracts: 8.
- Contracts after scan gates: 7.
- Low-liquidity contracts with open interest: 3.
- Vertical spread candidates: 4.
- Multi-snapshot replay fixture: `DATA/replay/silver_option_quote_replay.csv`.
- Quote replay snapshots: 12.
- Quote replay spread candidates: 2.
- Replay first-leg fills: 1.
- Replay incomplete legs: 1.
- Replay stale quote observations: 2.
- Replay CSV: `REPORTS/quant_baseline_replay.csv`.
- Missing data: real tick series, full order book depth, transaction logs, margin schedule, fee schedule by venue, and statistically meaningful historical samples.

## Can It Answer The Key Question?

只能做仓库 fixture 级 replay 判断，不能做统计结论；当前多快照样本回放 2 组候选，第一腿成交 1 组，不完整腿 1 组，静态平均模拟改善 2.398 点。

Key question: Does passive first-leg plus active second-leg simulation improve combo net price versus immediate baseline after costs?

- Current average simulated improvement: 2.398.
- Accepted simulated spreads: 3.
- Rejected simulated spreads: 1.
- Worst simulated second-leg slippage: 3.2571.
- Reliability: `LOW_SAMPLE`.
- Risk flags: `LOW_PASSIVE_FILL, LOW_SAMPLE, WIDE_LEG_SPREAD`.

## Remaining Gaps

- Replace the TASK-010 fixture with larger repository-local historical samples once safe, non-account data is available.
- Add option-chain metadata and robust symbol parser for domestic silver option naming variants.
- Add成交回报 fixture so passive-fill and incomplete-leg rates can be validated against fills, not only quote-state assumptions.
- Add parameter sensitivity over fill threshold, maximum adverse move, timeout, and second-leg slippage.
- Add dashboard tables for time-value anomalies, spread ranking, and replay summary.

## Verification

- python3 scripts/refresh_visible_status.py: passed.\n- bash scripts/check_worker_health.sh: passed.\n- python3 -m compileall -q src tests scripts: passed.\n- python3 -m unittest discover -s tests: passed, 17 tests.\n- bash -n scripts/codex_worker.sh: passed.

## Next Three Safe Codex Tasks

1. TASK-011: Add parameter sensitivity report for passive fill threshold, timeout, second-leg max adverse move, fee and slippage assumptions.
2. TASK-012: Extend visible dashboard/report layer with time-value anomaly table, spread ranking table, and replay summary link.
3. TASK-013: Add safe repository-local fill-event fixture to validate passive-fill and incomplete-leg assumptions without connecting any broker account.
