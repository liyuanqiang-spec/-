# DATA_SCHEMA.md

Current mode: `PHASE_1_SIMULATION_ONLY`

This file is the canonical field contract for safe data ingestion, cleaning,
scanning, backtesting, simulated fills, and reporting. It does not authorize or
describe real broker login, real order placement, real cancellation, fund
transfer, or raw-data deletion.

## Conventions

| Rule | Standard |
|---|---|
| Encoding | UTF-8 CSV or UTF-8 markdown unless a source format requires otherwise |
| Field names | `snake_case` |
| Timezone | Exchange-local time; default processing timezone is `Asia/Shanghai` |
| Date format | `YYYY-MM-DD` |
| Datetime format | ISO 8601 string, preferably with timezone offset |
| Numeric format | Decimal number without comma separators |
| Missing values | Empty string in raw CSV; converted to `None` during cleaning |
| Contract code field | Use `symbol` as the canonical project field |
| Option type | `C` for call, `P` for put |
| Side | `buy` or `sell` |
| Offset | `open`, `close`, `close_today`, `close_yesterday`, or empty if unknown |
| Data source | `sample`, `import`, `exchange`, `broker_export`, `manual`, or `simulation` |

## Current MVP Scanner Input

The existing scanner can run with one contract snapshot table. This is the
minimum required input for `src/codex_quant.contract_scanner.load_contracts`.

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| symbol | string | yes | non-empty | Option contract code |
| underlying | string | yes | non-empty | Underlying futures code |
| expiry | date | yes | valid date string | Expiration date |
| strike | float | yes | greater than 0 | Strike price |
| option_type | enum | yes | `C` or `P` | Option direction |
| bid | float | yes | greater than or equal to 0 | Best bid used by scanner |
| ask | float | yes | greater than `bid` | Best ask used by scanner |
| volume | int | yes | greater than or equal to 0 | Session or daily volume |
| open_interest | int | yes | greater than or equal to 0 | Open interest |

## Option Daily Fields

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | yes | non-empty | Option contract code |
| exchange | string | no | non-empty if present | Example: `SHFE` |
| underlying | string | yes | non-empty | Underlying futures code |
| underlying_symbol | string | no | non-empty if present | Explicit futures contract when different from `underlying` |
| expiry | date | yes | valid date string | Expiration date |
| option_type | enum | yes | `C` or `P` | Call or put |
| strike | float | yes | greater than 0 | Strike price |
| open | float | no | greater than or equal to 0 | Daily open |
| high | float | no | greater than or equal to 0 | Daily high |
| low | float | no | greater than or equal to 0 | Daily low |
| close | float | yes | greater than or equal to 0 | Daily close |
| settlement | float | no | greater than or equal to 0 | Exchange settlement price |
| pre_settlement | float | no | greater than or equal to 0 | Previous settlement |
| volume | int | yes | greater than or equal to 0 | Daily traded contracts |
| turnover | float | no | greater than or equal to 0 | Daily turnover if available |
| open_interest | int | yes | greater than or equal to 0 | End-of-day open interest |
| open_interest_change | int | no | integer | Change from previous trading day |
| upper_limit | float | no | greater than or equal to 0 | Daily upper price limit |
| lower_limit | float | no | greater than or equal to 0 | Daily lower price limit |
| source | enum | yes | known source value | Raw data source |
| ingestion_ts | datetime | no | valid datetime string | Time imported into project |

## Tick Fields

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| ts | datetime | yes | valid datetime string | Exchange timestamp |
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | yes | non-empty | Contract code |
| exchange | string | no | non-empty if present | Exchange code |
| last_price | float | yes | greater than or equal to 0 | Last traded price |
| last_volume | int | no | greater than or equal to 0 | Last tick volume if available |
| volume | int | yes | greater than or equal to previous tick | Cumulative session volume |
| turnover | float | no | greater than or equal to 0 | Cumulative turnover |
| open_interest | int | no | greater than or equal to 0 | Current open interest |
| bid_price_1 | float | no | greater than or equal to 0 | Best bid at tick time |
| bid_volume_1 | int | no | greater than or equal to 0 | Best bid size |
| ask_price_1 | float | no | greater than or equal to 0 | Best ask at tick time |
| ask_volume_1 | int | no | greater than or equal to 0 | Best ask size |
| source | enum | yes | known source value | Raw data source |

## Order Book Fields

Use this schema for quote snapshots and order book snapshots. Level 1 is required for
liquidity scans. Levels 2-5 are optional and should follow the same pattern.

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| ts | datetime | yes | valid datetime string | Quote timestamp |
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | yes | non-empty | Contract code |
| exchange | string | no | non-empty if present | Exchange code |
| bid_price_1 | float | yes | greater than or equal to 0 | Best bid |
| bid_volume_1 | int | yes | greater than or equal to 0 | Best bid size |
| ask_price_1 | float | yes | greater than or equal to 0 | Best ask |
| ask_volume_1 | int | yes | greater than or equal to 0 | Best ask size |
| bid_price_2 | float | no | greater than or equal to 0 | Second bid level |
| bid_volume_2 | int | no | greater than or equal to 0 | Second bid size |
| ask_price_2 | float | no | greater than or equal to 0 | Second ask level |
| ask_volume_2 | int | no | greater than or equal to 0 | Second ask size |
| bid_price_3 | float | no | greater than or equal to 0 | Third bid level |
| bid_volume_3 | int | no | greater than or equal to 0 | Third bid size |
| ask_price_3 | float | no | greater than or equal to 0 | Third ask level |
| ask_volume_3 | int | no | greater than or equal to 0 | Third ask size |
| bid_price_4 | float | no | greater than or equal to 0 | Fourth bid level |
| bid_volume_4 | int | no | greater than or equal to 0 | Fourth bid size |
| ask_price_4 | float | no | greater than or equal to 0 | Fourth ask level |
| ask_volume_4 | int | no | greater than or equal to 0 | Fourth ask size |
| bid_price_5 | float | no | greater than or equal to 0 | Fifth bid level |
| bid_volume_5 | int | no | greater than or equal to 0 | Fifth bid size |
| ask_price_5 | float | no | greater than or equal to 0 | Fifth ask level |
| ask_volume_5 | int | no | greater than or equal to 0 | Fifth ask size |
| source | enum | yes | known source value | Raw data source |

## Trade Fields

Use this schema for imported historical trades, backtest fills, and simulated fills.
Real broker-side order IDs must not be required in this phase.

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| trade_id | string | yes | unique inside source file | Simulated or imported trade id |
| order_id | string | no | empty for unavailable ids | Simulated or imported order id |
| ts | datetime | yes | valid datetime string | Trade time |
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | yes | non-empty | Contract code |
| exchange | string | no | non-empty if present | Exchange code |
| side | enum | yes | `buy` or `sell` | Fill side |
| offset | enum | no | known offset or empty | Open/close flag |
| price | float | yes | greater than 0 | Fill price |
| quantity | int | yes | greater than 0 | Filled contracts |
| fee | float | no | greater than or equal to 0 | Fee charged or simulated |
| slippage | float | no | decimal number | Simulated slippage per contract |
| source | enum | yes | known source value | `import` or `simulation` in this phase |
| strategy_id | string | no | non-empty if present | Strategy that produced the fill |
| note | string | no | free text | Human-readable explanation |

## Position Fields

Use this schema for imported snapshots, simulated positions, and backtest
holdings. All fields are informational in this phase.

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| as_of | datetime | yes | valid datetime string | Snapshot time |
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | yes | non-empty | Contract code |
| exchange | string | no | non-empty if present | Exchange code |
| direction | enum | yes | `long` or `short` | Position direction |
| quantity | int | yes | greater than or equal to 0 | Current position size |
| available_quantity | int | no | greater than or equal to 0 | Quantity available to close in simulation or import |
| avg_price | float | no | greater than or equal to 0 | Average cost |
| settlement_price | float | no | greater than or equal to 0 | Current settlement mark |
| last_price | float | no | greater than or equal to 0 | Current last price mark |
| market_value | float | no | decimal number | Marked position value |
| unrealized_pnl | float | no | decimal number | Simulation/backtest PnL only |
| source | enum | yes | known source value | Raw data source |
| strategy_id | string | no | non-empty if present | Strategy bucket |

## Margin Fields

Margin fields are for exchange/broker-export assumptions and simulation risk
checks only. They must not trigger margin movement or account actions.

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | yes | non-empty | Contract code |
| exchange | string | no | non-empty if present | Exchange code |
| product | string | no | non-empty if present | Product code, example `ag` |
| margin_per_contract | float | yes | greater than or equal to 0 | Absolute margin assumption |
| margin_rate | float | no | between 0 and 1 when present | Rate-based margin assumption |
| long_margin_rate | float | no | between 0 and 1 when present | Long-side rate |
| short_margin_rate | float | no | between 0 and 1 when present | Short-side rate |
| contract_multiplier | float | no | greater than 0 | Contract multiplier |
| currency | string | no | ISO-like code if available | Example: `CNY` |
| source | enum | yes | known source value | `exchange`, `broker_export`, `sample`, or `simulation` |

## Fee Fields

Fee fields are for backtest and simulation assumptions. They must not require
secret access or paid broker calls.

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| trade_date | date | yes | `YYYY-MM-DD` | Trading date |
| symbol | string | no | non-empty if present | Contract-level fee when available |
| exchange | string | no | non-empty if present | Exchange code |
| product | string | yes | non-empty | Product code, example `ag` |
| fee_open | float | yes | greater than or equal to 0 | Open fee per contract or rate |
| fee_close | float | yes | greater than or equal to 0 | Close fee per contract or rate |
| fee_close_today | float | no | greater than or equal to 0 | Close-today fee if applicable |
| fee_unit | enum | yes | `per_contract`, `by_notional`, or `by_turnover` | How fee is applied |
| min_fee | float | no | greater than or equal to 0 | Minimum fee if applicable |
| currency | string | no | ISO-like code if available | Example: `CNY` |
| source | enum | yes | known source value | `exchange`, `broker_export`, `sample`, or `simulation` |

## Validation Gates

| Gate | Rule |
|---|---|
| Required fields | Stop cleaning or scanning when any required field is missing |
| Bad prices | Exclude rows where required prices are negative or ask is not greater than bid |
| Stale quotes | Exclude quote snapshots older than the configured scan window |
| Wide spreads | Exclude or mark high risk according to strategy config |
| Missing legs | Stop simulated spread construction when any required leg is absent |
| Unknown source | Keep the row out of production reports until mapped |
| Raw data | Never delete original/raw input; write cleaned output separately |
| Secrets | Reject columns that contain passwords, tokens, API keys, or account credentials |

## Suggested File Mapping

| Dataset | Suggested path |
|---|---|
| Option daily | `DATA/raw/option_daily.csv` or `data/raw/option_daily.csv` |
| Tick | `DATA/raw/ticks.csv` or `data/raw/ticks.csv` |
| Order book | `DATA/raw/order_book.csv` or `data/raw/order_book.csv` |
| Trades | `DATA/raw/trades.csv` or `data/raw/trades.csv` |
| Positions | `DATA/raw/positions.csv` or `data/raw/positions.csv` |
| Margin | `DATA/raw/margin.csv` or `data/raw/margin.csv` |
| Fees | `DATA/raw/fees.csv` or `data/raw/fees.csv` |
| Cleaned data | `DATA/clean/` or `data/clean/` |
