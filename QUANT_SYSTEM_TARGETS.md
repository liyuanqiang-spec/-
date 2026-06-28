# QUANT_SYSTEM_TARGETS.md

This file is the standing target for the quant system work. It consolidates prior ChatGPT discussions, uploaded project documents, and the current repository status.

## 1. North star

Build a silver-option market-microstructure execution research system.

The system is not a price-prediction model. It studies whether low-liquidity option spreads can be improved by:

1. scanning option chains,
2. generating vertical-spread candidates,
3. ranking candidates by executable edge,
4. simulating passive first-leg fills,
5. simulating active second-leg completion,
6. replaying logs, and
7. reporting whether net execution improvement is positive after costs.

Current phase: research, simulation, replay, reporting, and repository-local software improvement.

## 2. Core strategy definition

Primary product: silver options and related silver futures.

Primary structure: vertical option spreads.

First-stage focus: position close-out optimization and small-sample validation before any broader two-sided market-making design.

Core idea:

- Low-liquidity leg has wider bid-ask spread.
- The system tests candidate prices inside the spread.
- After the first leg fills in simulation, the more liquid leg is completed in simulation.
- The result is compared with an immediate execution baseline.

Core formulas:

```text
combo_net_price = leg_a_actual_price - leg_b_actual_price
immediate_baseline = leg_a_bid1 - leg_b_ask1
execution_improvement = combo_net_price - immediate_baseline
```

For opening or alternative spread direction, the same idea must be normalized into a signed combo formula and documented.

## 3. Required system modules

Codex should build or improve these modules in the repository, preserving existing work:

1. Data loader
   - futures quote CSV
   - option quote CSV
   - option chain metadata
   - simulated fill events
   - local replay logs

2. Contract parser
   - underlying
   - expiry
   - option type
   - strike
   - call/put pairing

3. Time-value radar
   - intrinsic value
   - buy time value
   - sell time value
   - mid time value
   - bid-ask spread
   - spread percentage
   - parity deviation

4. Low-liquidity scanner
   - wide-spread ranking
   - open-interest filter
   - volume and depth filter
   - stale quote filter
   - quote-quality flags

5. Combination generator
   - vertical spread candidates
   - anchor-leg selection
   - strike traversal
   - same-expiry grouping
   - call and put variants

6. Scoring engine
   - expected_edge
   - fill_probability
   - liquidity_score
   - risk_score
   - fee and slippage assumptions
   - second-leg cost estimate
   - minimum edge threshold

7. State machine simulator
   - IDLE
   - FOUND
   - PENDING_FIRST_LEG
   - FIRST_LEG_FILLED
   - HEDGING_SECOND_LEG
   - DONE
   - COOLDOWN
   - FAILED

8. Second-leg protection simulator
   - signed combo formula
   - reserved net price
   - maximum adverse move
   - timeout handling
   - partial-fill handling

9. Replay and reporting
   - candidate count
   - accepted and rejected candidates
   - fill rate
   - incomplete-leg rate
   - average net improvement
   - worst simulated slippage
   - maximum adverse move
   - parameter sensitivity
   - Markdown and CSV reports

10. Dashboard or app
   - data source status
   - latest update time
   - option chain table
   - time-value abnormal list
   - spread ranking
   - low-liquidity candidates
   - parity deviations
   - simulation summary

## 4. Existing software positioning

Use existing trading and analysis software as references or external execution environments only. Do not rebuild everything.

- InfiniTrader / 无限易: preferred execution-side reference; useful for custom spreads, priority leg logic, PythonGo, DDE/RTD, and quote export.
- Kua期3 / 快期3: useful for T-style option view, dynamic export, time-value observation, and expiry/self-hedge review.
- WingChun / 咏春 and Huidian / 汇点: useful for Greeks, IV, matrix view, PnL, and risk analysis.

Repository code should focus on what must be self-built:

- time-value radar,
- low-liquidity scanner,
- executable-spread judgment,
- anti-chasing state machine,
- second-leg net-price protection simulator,
- log replay,
- parameter reporting.

## 5. Anti-chasing principles

Radar can be sensitive, but simulated execution must be disciplined.

Rules:

- One active task per combination.
- Existing active candidate suppresses duplicate triggers.
- Do not treat own quote impact as an external opportunity change.
- Do not react to every one-tick competitor move.
- Repricing should be evaluated by time interval and edge improvement.
- Candidate exits only when edge is invalid, second-leg completion is not acceptable, risk limit is exceeded, or waiting time is exceeded.

## 6. Safety boundaries

The repository remains in PHASE_1_SIMULATION_ONLY.

Allowed:

- sample data,
- historical data,
- local CSV files,
- replay logs,
- simulation,
- dashboards,
- reports,
- tests,
- repository-local scripts.

Not allowed without explicit later approval:

- connecting to broker endpoints,
- sending broker instructions,
- changing broker permissions,
- storing credentials,
- modifying machine-level settings,
- deleting original data.

## 7. Immediate P0 target

After communication reliability is fixed, the next quant-system target is not generic software cleanup. The target is:

```text
Build a repository-local quant-system baseline that compares the current repo against this target, implements the safest missing pieces, and reports the remaining gap.
```

Expected report:

```text
REPORTS/quant_system_gap_report.md
```

The report must include:

1. modules already implemented,
2. modules missing,
3. tests passing or failing,
4. sample data coverage,
5. next three Codex tasks,
6. whether the current system can answer the key question:

```text
Does passive first-leg plus active second-leg simulation improve combo net price versus immediate baseline after costs?
```

## 8. Acceptance criteria for the next Codex pass

The next pass is successful if:

1. `TASK_QUEUE.md` marks the task completed.
2. `REPORTS/quant_system_gap_report.md` exists.
3. `WORKER_DASHBOARD.md` and `GPT_VISIBLE_STATUS.md` are refreshed.
4. Health check passes or explains the exact failing item.
5. Unit tests and compile checks pass or list exact failures.
6. The system has a clear next task queue for the missing quant modules.
