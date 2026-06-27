# DATA_SCHEMA.md

Current mode: `PHASE_1_SIMULATION_ONLY`

## Option Daily Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| trade_date | date | yes | Trading date |
| symbol | string | yes | Option contract code |
| underlying | string | yes | Underlying futures code |
| expiry | date | yes | Expiration date |
| option_type | string | yes | `C` or `P` |
| strike | float | yes | Strike price |
| open | float | no | Daily open |
| high | float | no | Daily high |
| low | float | no | Daily low |
| close | float | yes | Daily close |
| settlement | float | no | Settlement price |
| volume | int | yes | Daily volume |
| open_interest | int | yes | Open interest |

## Tick Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| ts | datetime | yes | Exchange timestamp |
| symbol | string | yes | Contract code |
| last_price | float | yes | Last traded price |
| volume | int | yes | Cumulative volume |
| open_interest | int | no | Current open interest |

## Order Book Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| ts | datetime | yes | Quote timestamp |
| symbol | string | yes | Contract code |
| bid_price_1 | float | yes | Best bid |
| bid_volume_1 | int | yes | Best bid size |
| ask_price_1 | float | yes | Best ask |
| ask_volume_1 | int | yes | Best ask size |
| bid_price_n | float | no | Deeper book levels |
| ask_price_n | float | no | Deeper book levels |

## Trade Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| trade_id | string | yes | Simulated or imported trade id |
| ts | datetime | yes | Trade time |
| symbol | string | yes | Contract code |
| side | string | yes | buy/sell |
| offset | string | no | open/close |
| price | float | yes | Fill price |
| quantity | int | yes | Contracts |
| source | string | yes | sample/import/simulation |

## Position Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| as_of | datetime | yes | Snapshot time |
| symbol | string | yes | Contract code |
| direction | string | yes | long/short |
| quantity | int | yes | Position size |
| avg_price | float | no | Average cost |
| unrealized_pnl | float | no | Simulation only |

## Margin Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| trade_date | date | yes | Trading date |
| symbol | string | yes | Contract code |
| margin_per_contract | float | yes | Simulation assumption |
| margin_rate | float | no | If available |
| source | string | yes | exchange/broker/sample |

## Fee Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| trade_date | date | yes | Trading date |
| symbol | string | yes | Contract code |
| fee_open | float | yes | Open fee assumption |
| fee_close | float | yes | Close fee assumption |
| fee_close_today | float | no | If applicable |
| source | string | yes | exchange/broker/sample |
