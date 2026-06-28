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
