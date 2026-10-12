# Paper Methods — FSR Securitization for Hotels and Flights

Consolidated record of the methods used across this research programme, so the
approach survives any cleanup of the original working tree. Companion material:
`docs/reference/` holds the P0 experiment scripts and the revision plan.

---

## 0. Research framing

**Future Service Rights (FSR)** — a tokenized claim on one future unit of
perishable service capacity. Two instances are studied together:

| | Hotel | Flight |
|---|---|---|
| Capacity unit | room-night | seat |
| Issuer | individual hotel | carrier |
| Data source | Chengdu OTA price panel | U.S. DOT DB1B survey |
| Dependence | Gaussian copula | multivariate t-copula (ν = 4) |
| Maturity | 36 months | 12 months |

The unit of the framework is a **Time-Right (TR)**: it trades on a secondary
market and settles by cash, discounted physical stay/travel, or transfer.

---

## 1. Economic mechanism (both markets)

- Platform acts as market maker: buys wholesale at `P_issue`, sells retail at
  `P_retail`; discount is market-driven, the supplier pays zero commission.
- Issuance value = room count (or seats) × days × over-issuance multiple.
- Settlement mechanisms:
  - **Continuous offset** (primary) — sell anytime; proceeds apply as booking
    credit. User share 45%.
  - **Ternary physical** (floor) — at maturity, fixed α = 0.70. User share 30%.
  - **Cash / transfer** — contractual or market. User share 25%.
- Flight variant simplifies redemption to cash 70% / voucher 25% / transfer 5%
  and adds a **carrier buyback** below 82% of issue price (implicit price floor).

Stakeholder split is reported per Time-Right (hotel baseline: system
+¥1,227/TR; hotels +¥817, users +¥221, platform +¥98, investors +¥91).

---

## 2. Structured-finance engine (the system contribution)

Shared pipeline: **asset pool → stratification → credit model → dependence
sampling → cash-flow waterfall → tranche loss → rating**.

**Tranches.** Hotel: senior/mezzanine/junior/equity with reserve and
overcollateralization. Flight: 65% / 20% / 10% / 5%, coupons 5.5% / 8.0% / 12.0%,
reserve 5%, OC 3%.

**Waterfall.** Sequential-pay with OC/IC triggers and acceleration; losses
propagate bottom-up (junior absorbs first, senior last), with LGD recovery.

**Dependence.** Defaults sampled via copula of default times.
- Hotel: Gaussian copula.
- Flight: t-copula ν = 4 with a correlation matrix estimated from 5-year daily
  airline equity log-returns (2021–2025, 1,192 days).

**Monte Carlo.** 2,000–5,000 paths; joblib-parallel; VaR 95/99; stress
multipliers (Baseline → Extreme).

### 2.1 Algorithm A1 — copula normalisation (critical fix)

Correlated latent draws must satisfy

```
u = c · Z · w + ε · (1 − w),      require  var(u) = 1
```

If `var(u) ≠ 1`, then `Φ(u)` is **not** uniform, and the realized default rate is
systematically biased. Measured bias in the original build: ~3× at true
`p = 0.056` and ~42× at `p = 0.001`. This is a first-class algorithmic detail of
the paper, not an implementation footnote.

### 2.2 Algorithm A2 — waterfall

Per period: collect → pay senior coupon/principal → mezzanine → junior → equity,
with OC/IC breach tests switching to accelerated amortisation. Write the state
transition explicitly in pseudo-code for the paper.

### 2.3 Algorithm A3 — stratified asset-pool sampling

Stratify by level (hotel) / distance band (flight) with concentration caps.
Note `max(int(target × weight), 5)` makes the realized pool size differ from the
target (e.g. 66 → 64); state this in the paper.

### 2.4 Algorithm A4 — period-differentiated pricing

Three price tiers (holiday / weekend / weekday); issuance volume = rooms × days ×
over-issuance multiple.

---

## 3. Credit modelling

### 3.1 Structural baseline (and its failure)

Merton DD + GARCH with a PD cap (0.50). KMV variant. On this borrower set the
structural models **fail**: 65/66 pooled names hit the 50% cap, and three
specifications span 9.8% → 49.4% → 98.2% (10× spread). The root cause is
**uninformative inputs** — volatility-based DD has near-zero signal on this panel
(AUC ≈ 0.51).

### 3.2 Data-calibrated PD (hotel)

Survival / platform-exit analysis over 14,851 hotels observed Mar–Jun 2024:

| Tier | 3-month exit rate | Calibrated PD |
|---|---|---|
| Economy | 9.00% | 15.7% |
| Comfort | 3.62% | 6.8% |
| Upscale | 1.30% | 2.5% |
| Luxury | 0.00% | 0.5% |

Under calibrated PDs, MC yields Senior EL 0.16%, VaR99 3.98% → Aa–A.

### 3.3 Machine-learning PD (the new core contribution)

**Task.** Binary: from a hotel's month-*t* price-panel features, predict whether
it has **exited the platform** by *t+3* months.

**Data.** Panel of 16,257 hotels × 4 months. Rolling cohorts t ∈ {Mar, Apr, May}.
Label = absent from the t+3 panel.

**Labelling caveat (state explicitly).** Exit ≠ default; it is a measurable,
assumption-light *proxy*. The 4-month window cannot support true out-of-time
validation. Main task predicts exit; the exit→default mapping is handled as a
sensitivity, not baked in.

**Features.** price level (mean/median/min/max); volatility (log-return sd,
annualised vol, range ratio); trend (monthly change, slope, momentum); shape
(weekly cycle, intra-month variation, seasonal residual); completeness
(n_records, days present, span); structure (price band, district, lat/lon);
competition (same-district same-tier hotel count from the 86,159-row directory).

**Models.** Logistic regression baseline; Random Forest / LightGBM / XGBoost;
GRU on price sequences. Structural baselines: Merton DD, KMV.

**Evaluation (deliberately not AUC-only).** Discrimination: AUC, PR-AUC.
Calibration: Brier score, ECE, reliability diagram. Threshold behaviour.

**P0 empirical results** (Chengdu, Mar→Jun cohort, N = 14,851, positive 7.84%):

| Configuration | AUC | PR-AUC |
|---|---|---|
| All features | 0.8290 | 0.3843 |
| Drop completeness | 0.7930 | 0.3071 |
| Drop completeness + geography | 0.7808 | 0.2776 |
| Price features only | 0.7474 | 0.2485 |
| Completeness only (control) | 0.7401 | 0.2648 |
| Geography only (control) | 0.5813 | 0.1034 |
| Best single economic feature (price_mean) | 0.6522 | — |
| Merton DD (structural) | 0.5644 | — |

Signal exists (AUC ≫ 0.5). Completeness is the strongest single group and is a
known confound, **but price-only features still reach 0.747**, so the model does
not depend on it.

**Calibration finding (contribution #3).** With all features, AUC spread across
seven configurations is only **0.0355**, while ECE spread is **0.3050 (≈50×)**.
`class_weight='balanced'` barely changes discrimination but breaks calibration
(logistic-regression mean predicted PD inflated **5.0×**); isotonic calibration
repairs it (ECE 0.0943 → 0.0100) without hurting AUC. Downstream, a 5× PD bias
propagates to a ~5× bias in tranche expected loss — this is the bridge from ML to
the financial application.

---

## 4. Flight extension

**Data.** U.S. DOT DB1B Origin-and-Destination (Market) survey, 13 quarters
2022Q1–2025Q1: 97.3M records, 102,279 OD routes, 25 carriers. Route pool built by
stratified sampling over distance bands (short/medium/long), capped per carrier.

**Pricing.** Booking curve replaces spot convergence:
`P(t) = P₀ · exp(β · t / T)`, β = 0.22. Discount rate `r₀ = 8%` (airline WACC);
issue discount 8%; safety factor 0.82.

**Result.** 69-route pool across 11 carriers; Senior tranche EL 0 bps, rating
Aaa–Aa; maximum pool loss 15.6% never breaches the 35% subordination.
Robust across Gaussian, t(6) and t(4) copulas and `r₀ ∈ [4%, 12%]`.

**Known limitation.** DB1B records tickets by travel quarter, not purchase date,
so β cannot be calibrated from the data; user savings are shown to be
independent of β by algebraic construction.

---

## 5. Competition paradox (cross-market hypothesis)

In DB1B, route fare dispersion (`fare_cv`) *rises* with the number of carriers
`n_carriers` — a paradox versus standard competition intuition. The same test is
runnable on the hotel panel: price dispersion within a district × tier cell
versus hotel density. Testing one hypothesis on both markets is the natural
basis for a combined hotel + flight paper.

---

## 6. Positioning of the new paper

Shift from "a new asset class" (mechanism design) to a **simulation-system**
paper for a CS/EI venue: architecture + algorithms (copula sampling, waterfall,
stratified sampling, parallel Monte Carlo) + a machine-learning PD component
validated on 1.7M real price records. Three contributions:

1. **System / algorithms** — FSR securitization simulator with copula-dependent
   default sampling, OC/IC waterfall, parallel MC; pseudo-code + complexity +
   speed-up.
2. **ML PD** — replaces structural models that fail on sparse borrowers.
3. **Calibration over discrimination** — probability-calibration quality, not
   ranking, determines tranche ratings.

**Reported limitations.** (i) 4-month window, no out-of-time validation;
(ii) exit ≠ default, proxy label is noisy; (iii) prototype is an offline
simulation, not a chain deployment.

---

## 7. Reference assets in this repository

| File | What it is |
|---|---|
| `docs/reference/REVISION_PLAN.md` | Section-by-section rewrite plan with all P0 results |
| `docs/reference/p0_feasibility.py` | Feasibility experiment: can exit be predicted? |
| `docs/reference/p0_baselines.py` | Feature ablation, single-feature and structural baselines |
| `docs/reference/p05_calibration.py` | Discrimination-vs-calibration experiment (contribution #3) |
