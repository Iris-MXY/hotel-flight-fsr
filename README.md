# Hotel & Flight FSR — Research Data

Source data for a research paper that applies the **Future Service Rights (FSR)**
framework to **two markets at once**: hotel room-nights and airline seat-nights.

An FSR is a tokenized claim on one future unit of perishable service capacity.
Hotel room-nights and flight seats are the two canonical instances, which is why
they are studied together.

The repository holds the **data package** (analysis-ready tables + the code
needed to fetch the raw inputs) and a written record of the **paper methods**
under `docs/`. The simulation engine and manuscript are built on top of this
package.

## Repository layout

```
data/           analysis-ready datasets (see inventory below)
scripts/        download_db1b.py - fetch + verify the raw DB1B quarters
docs/           PAPER_METHODS.md + reference material for the paper
```

---

## Data inventory

| Path | Size | Rows | Content |
|---|---:|---:|---|
| `data/hotel/cleaned_hotel_prices.csv` | 51.3 MB | 1,707,918 | Cleaned daily price panel: `date`, `hotelCode`, `price` (price in **fen**) |
| `data/hotel/2024_3.csv` … `2024_6.csv` | ~13.8 MB each | ~0.43 M each | Raw daily prices, Mar–Jun 2024 (source for the cleaned panel) |
| `data/hotel/hotel_info.csv` | 6.3 MB | 86,159 | Hotel metadata: `hotelName`, `hotelLevel`, `lon经度`, `lat纬度` |
| `data/hotel/hotel_future_prices.csv` | 0.3 MB | 16,257 | Derived forward price per hotel: `hotelCode`, `futurePrice` |
| `data/flight/flight_routes_real.csv` | 2.1 MB | 25,872 | Route-level stats from DB1B 2024Q2: `mean_fare`, `std_fare`, `fare_cv`, `n_carriers`, distance band, carrier list |
| `data/flight/flight_eda_v4_summary.json` | 7 KB | — | Full DB1B EDA summary: 13 quarters (2022Q1–2025Q1), 97.3 M rows, 102,279 routes, 25 carriers |
| `data/flight/empirical_carrier_correlations.json` | 2 KB | — | 9-carrier equity-return correlation matrix (5-yr daily, 2021–2025) |
| `data/flight/flight_fsr_results_v1.json` | 55 KB | — | Flight FSR engine output (Monte Carlo / tranche results) |
| `data/flight/db1b_manifest.json` | 2 KB | — | The 13 DB1B quarters: file names, URLs, byte sizes |
| `data/provenance/*.py` | — | — | Scripts that produced the flight aggregates (kept for provenance) |

Column-by-column descriptions and SHA-256 checksums are in
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

---

## Hotel data

- Coverage: **16,257 hotels**, daily prices **2024-03-01 … 2024-06-30** (Chengdu, China).
- `2024-03` alone contains exactly **14,851** hotels — the cohort size used in the
  survival / platform-exit analysis.
- Price unit is **fen** (1/100 CNY); median 16,700 = ¥167 per night.
- `hotelLevel` takes the four values `经济` / `舒适` / `高档` / `豪华`
  (Economy / Comfort / Upscale / Luxury).

The panel supports: price-level, volatility, trend, and seasonality features;
a platform-exit label (a hotel absent from a later month's panel); and local
competition density (hotels per district and level, from the 86,159-row metadata).

## Flight data

The raw source is the U.S. DOT **DB1B** Origin-and-Destination Survey (Market),
a 10% quarterly sample of domestic U.S. tickets. It is public:
<https://www.transtats.bts.gov/>

> The **raw DB1B zips are not stored here.** They are 78–105 MB each (~1.27 GB
> across 13 quarters) and three of them exceed GitHub's 100 MiB per-file limit.
> Fetch and verify them with:
>
> ```bash
> python scripts/download_db1b.py --unzip
> ```
>
> The download is resumable and checks every file against the byte counts in
> `data/flight/db1b_manifest.json`. To rebuild `flight_routes_real.csv` from the
> raw zips, run `data/provenance/extract_real_routes.py`.

Key facts from the flight EDA: 97.3 M fare observations, 102,279 OD routes,
25 carriers, mean fare CV ≈ 0.56.

---

## Provenance

Extracted from the local working tree of `hotel-order-financialization`
(`https://github.com/David-coder-hnu/hotel-order-financialization`), commit
`4be93ae`. The hotel CSVs were copied byte-for-byte; every SHA-256 checksum is
recorded in `DATA_DICTIONARY.md`.

## License

MIT — see [`LICENSE`](LICENSE).
