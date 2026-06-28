# Silver Option Quote Replay Fixture

`silver_option_quote_replay.csv` is a repository-local, simulation-only quote replay fixture for TASK-010.

It contains multiple ordered snapshots for two silver option vertical spread candidates that already exist in `DATA/contracts/sample_options.csv` after the scanner gates:

- `AG2608C7200` / `AG2608C7400`
- `AG2608P7200` / `AG2608P7000`

Fields:

- `snapshot_id`, `timestamp`: ordered replay clock.
- `bid`, `ask`, `bid_size`, `ask_size`, `bid_depth`, `ask_depth`: local quote and visible depth inputs.
- `quote_age_seconds`, `freshness_status`, `is_stale`: deterministic freshness and staleness controls.
- `source_note`: fixed provenance marker.

This file is not market data and must not be used as performance evidence. It exists only to validate loader, ordering, staleness, timeout, repricing, incomplete-leg, and second-leg protection behavior inside `PHASE_1_SIMULATION_ONLY`.

## TASK-011A Tick Smoke Fixture

`silver_option_tick_smoke.csv` is generated from `silver_option_quote_replay.csv` by `scripts/validate_offline_tick_files.py` when no repository-local historical tick CSV exists under the checked `DATA/raw/` or `data/raw/` paths.

It contains the required offline tick fields `datetime`, `symbol`, `bid_price1`, `bid_volume1`, `ask_price1`, `ask_volume1`, `last_price`, `volume`, `open_interest`, `trading_date`, and `source`, plus optional local depth/freshness fields when available. It is a sanitized compatibility fixture only, not historical market data.
