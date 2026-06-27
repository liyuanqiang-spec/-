---
name: market-data
description: Use for downloading, cleaning, validating, and inventorying market data for options, futures, spreads, and backtests.
---

# Market Data Skill

Use this skill for data download, cleaning, schema design, and data quality checks.

## Rules

1. Data work is allowed; real trading is not allowed.
2. Keep raw data immutable under `data/raw/`.
3. Write cleaned data under `data/clean/`.
4. Log source, time range, schema, missing values, and anomalies.
5. Never overwrite important data without a backup or explicit confirmation.

## Output

- Data source
- File paths
- Row counts
- Missing fields
- Cleaning notes
