# Data Dictionary

All hotel files are UTF-8 CSV with a header row. Flight aggregates use the
schemas described below. SHA-256 checksums are at the end of this document.

---

## Hotel

### `data/hotel/cleaned_hotel_prices.csv`

Cleaned daily price panel — the primary table for feature and label construction.

| Column | Type | Notes |
|---|---|---|
| `date` | string | `YYYY/M/D`, range 2024-03-01 … 2024-06-30 |
| `hotelCode` | string | Hotel id, e.g. `H00003179890` |
| `price` | float | Nightly rate in **fen** (1 CNY = 100 fen) |

Rows: 1,707,918 · Hotels: 16,257

### `data/hotel/2024_3.csv` … `2024_6.csv`

Raw daily prices as delivered, one file per month. Same `date` / `hotelCode` /
`price` columns plus trailing empty columns. Use these to re-derive the cleaned
panel or to audit cleaning decisions.

### `data/hotel/hotel_info.csv`

Hotel metadata for competition-density and location features.

| Column | Type | Notes |
|---|---|---|
| `hotelCode` | string | Join key to the price panel |
| `hotelName` | string | Display name |
| `hotelLevel` | string | `经济` / `舒适` / `高档` / `豪华` |
| `lon经度` | float | Longitude |
| `lat纬度` | float | Latitude |

Rows: 86,159 (whole-city directory, wider than the 16,257 priced hotels)

### `data/hotel/hotel_future_prices.csv`

Derived forward price per hotel.

| Column | Type | Notes |
|---|---|---|
| `hotelCode` | string | Hotel id |
| `futurePrice` | float | Forward rate in fen (derived) |

Rows: 16,257

---

## Flight

### `data/flight/flight_routes_real.csv`

Route-level statistics aggregated from DB1B 2024Q2 (routes with ≥ 20 obs).

| Column | Notes |
|---|---|
| `origin`, `dest`, `route` | OD airport codes and `origin-dest` label |
| `n_obs` | Ticket observations on the route |
| `total_pax` | Sum of sampled passengers |
| `mean_fare`, `std_fare` | Fare level and dispersion (USD) |
| `fare_cv` | `std_fare / mean_fare` |
| `n_carriers` | Distinct reporting carriers |
| `avg_distance`, `avg_coupons` | Mean miles flown and coupon count |
| `dist_band` | `short` / `medium` / `long` |
| `carriers_list` | Comma-separated carrier codes |

Rows: 25,872

### `data/flight/flight_eda_v4_summary.json`

Aggregate EDA over the full DB1B span (2022Q1–2025Q1): dataset totals, global
fare stats, concentration (carrier HHI, top-4 share), route-volatility stats,
per-carrier risk table, and per-quarter row/fare counts.

### `data/flight/empirical_carrier_correlations.json`

Carrier equity-return correlation matrix (9 carriers, 5-year daily log returns,
2021–2025, 1,192 trading days) used for the flight dependence structure.

### `data/flight/flight_fsr_results_v1.json`

Flight FSR engine output (Monte Carlo paths, tranche losses, stress and
sensitivity results).

### `data/provenance/*.py`

Scripts that produced the flight aggregates (`extract_real_routes.py`,
`flight_eda_v4.py`, `eda_12q_panel.py`, `eda_flight_full.py`). They reference an
external DB1B directory that is not part of this repository; adjust the path to
regenerate.

---

## SHA-256 checksums

| File | SHA-256 |
|---|---|
| `data/hotel/cleaned_hotel_prices.csv` | `0F355AB93A3178B700DF67F01B434621E707D1BD500AFA5743C9C421AB076879` |
| `data/hotel/2024_3.csv` | `E3F86B3B6161123012135FBA810725DB7F8AFDC16EAE945745EF142BBB22236B` |
| `data/hotel/2024_4.csv` | `183E65843F9CA86901A2F02FF5F07BC10D6FD1B43E3E81F0765EAA10E7767598` |
| `data/hotel/2024_5.csv` | `FBB868ED314E14857989FC0812F00848F685416913951D484FD17E4304823B74` |
| `data/hotel/2024_6.csv` | `CAE9805C13EB5583464DD93817F13D67379D5F1BCB845FED861A18FF952A9AFA` |
| `data/hotel/hotel_info.csv` | `468227A622CC92C9BCEB9D0B479BBD4F882D4625F3EB30F77D2FF2D2DD558402` |
| `data/hotel/hotel_future_prices.csv` | `47D74CC246FCB2D4CCFDCF3CFB0DDE66FF9828034A344D7131210130546D56CA` |
| `data/flight/flight_routes_real.csv` | `7985CB6D318DF175ACC498B3C0C4B4C8FB84C147E4C98247714D75ED980A1468` |
| `data/flight/flight_eda_v4_summary.json` | `F1FA897FC197D80A5644EE1039E7B4258D0B4114B105131EF939F715DAD6AF64` |
| `data/flight/empirical_carrier_correlations.json` | `B97BB7D93743B528516F6CA039E1F31E200E33DDE4D439374811DA327946F1E0` |
| `data/flight/flight_fsr_results_v1.json` | `6A0D5B04BF625F050D9685AA00C3C83C08F02080547C0B87393D216B1CD07372` |
