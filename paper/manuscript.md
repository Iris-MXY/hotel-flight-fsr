# A Simulation System for Future Service Rights Securitization

## Architecture, Algorithms, and Machine-Learning Credit Assessment

> Working draft. This Markdown file is the canonical manuscript source during P0/P1.
> The submission version will be exported to LaTeX after the experiment protocol is frozen.
>
> Status: outline plus draft text. `[TODO: ...]` marks missing evidence or citations.

**Keywords:** financial technology; asset securitization; Monte Carlo simulation;
credit risk; machine learning; probability calibration

---

## Abstract

Future service rights (FSR) turn a unit of perishable service capacity, such as a
hotel room-night or an airline seat, into a tradable claim. Securitizing these
claims requires a reliable estimate of default probability, but structural credit
models assume borrower-level asset values, debt structures, and sufficiently long
price histories that are rarely available for small service providers. We present
an offline simulation system for FSR securitization that combines copula-based
dependent default sampling, a cash-flow waterfall with overcollateralization and
interest-coverage triggers, stratified asset-pool construction, and parallel Monte
Carlo evaluation. For credit assessment, we recast probability of default as a
panel-learning problem and predict whether a hotel exits the platform three months
after the observation month. On a price panel covering 1,707,918 hotel-day records,
the model achieves AUCs from 0.8290 to 0.8956 across three cohorts. A dense-history
subsample shows that Merton and KMV baselines are weakly informative and frequently
hit the PD cap. We further show that discrimination and calibration can diverge
sharply: the AUC range across seven configurations is 0.0355, while the expected
calibration error range is 0.3050. Because tranche losses depend on absolute PD
levels rather than ranking alone, calibration is a first-order requirement for
connecting machine learning to securitization decisions.

---

## 1. Introduction

Hotel room-nights and airline seats are perishable inventory. Once the service
window passes, unused capacity has no value. Platforms and operators commonly sell
this capacity through uncertain future demand, while small suppliers face working
capital constraints. FSR provides a possible financing mechanism: a supplier issues
a claim on one future unit of capacity, and the platform or a secondary market
allocates that claim to users and investors.

The economic mechanism alone is not enough. A securitized pool needs a loss
distribution, a tranche structure, and a defensible estimate of default
probability. Structural credit models such as Merton distance-to-default and KMV
are natural baselines, but they require an asset-value process, a debt boundary,
and a sufficiently informative volatility signal. For individual hotels observed
through an online travel platform, these variables are absent. Our preliminary
experiments show that the available volatility signal is close to random on the
full cohort, and the structural baselines concentrate at the upper PD bound.

This paper makes three contributions:

1. We design an offline FSR securitization simulator with copula-based dependent
   default sampling, a trigger-aware cash-flow waterfall, stratified asset-pool
   construction, and parallel Monte Carlo evaluation.
2. We replace the structural PD core with a panel-feature learning model and
   evaluate it on 1.7 million real hotel-day price records.
3. We show that probability calibration, rather than discrimination alone,
   determines downstream tranche risk and rating behavior.

`[TODO: Add the frequent-flyer securitization precedent and the overbooking
literature in the introduction.]`

---

## 2. Related Work

### 2.1 Structural Credit Models

Merton models treat equity as a call option on the firm's assets and derive a
distance-to-default from asset value, debt, and volatility. KMV extends the same
logic with an empirical default boundary. These models are widely used for listed
firms but require inputs that are not observed for platform merchants.

`[TODO: Cite Merton (1974), KMV, and work on structural models with sparse data.]`

### 2.2 Machine Learning for Default Prediction

Tree ensembles and deep models have been applied extensively to credit scoring and
bankruptcy prediction. Most studies emphasize ranking metrics such as AUC, while
the downstream financial application depends on the absolute probability.

`[TODO: Cite logistic-tree credit scoring, credit-risk ML, and deep distress
prediction.]`

### 2.3 Probability Calibration

Brier scores, reliability diagrams, and expected calibration error measure whether
predicted probabilities match observed frequencies. Rebalancing can improve a
classifier's apparent minority-class sensitivity while damaging probability
calibration.

`[TODO: Cite classifier calibration survey, resampling and calibration, and
distribution-shift calibration.]`

### 2.4 Tokenized Assets and Service-Right Securitization

Tokenized real-world assets and frequent-flyer-backed financing are the closest
practical precedents for FSR. Overbooking and revenue-management models provide
the operational constraints under which future capacity is sold.

`[TODO: Cite AAdvantage, MileagePlus, SkyMiles, tokenized real estate, and
overbooking.]`

---

## 3. Problem Definition and System Overview

### 3.1 Future Service Rights

An FSR represents a claim on one unit of future perishable service capacity. The
two instances studied here are a hotel room-night and an airline seat. The basic
unit in the secondary market is a time-right (TR). A TR can be redeemed through
continuous offset, discounted physical service, or transfer.

The simulator is intentionally offline. It evaluates issuance, risk, and tranche
outcomes before any deployment decision. We do not claim that the prototype is
already deployed on-chain.

### 3.2 System Pipeline

The system pipeline is:

```text
asset pool -> stratified sampling -> credit model -> copula sampling
           -> cash-flow waterfall -> tranche losses -> rating
```

The platform acts as a market maker. The issuer sells future capacity at a
wholesale price, the platform retails the corresponding claims, and the cash-flow
engine allocates receipts across senior, mezzanine, junior, and equity tranches.

`[TODO: Insert the system architecture figure and state/data-flow description.]`

---

## 4. Algorithms

### 4.1 A1: Dependent Default Sampling

We sample latent variables through a copula and map them to default times. The
latent construction must preserve unit variance:

```text
u = c * Z * w + epsilon * (1 - w),    with Var(u) = 1
```

If `Var(u)` is not one, `Phi(u)` is not uniformly distributed and the realized
default rate is systematically biased. This normalization is a core implementation
requirement, not a cosmetic detail.

`[TODO: Add pseudocode and the measured bias for p = 0.056 and p = 0.001.]`

### 4.2 A2: Cash-Flow Waterfall

At each payment date, collected cash pays senior interest and principal first,
then mezzanine, junior, and equity. Overcollateralization and interest-coverage
tests can switch the structure into accelerated amortization. Losses propagate
from the bottom tranche upward.

`[TODO: Add the state-transition pseudocode.]`

### 4.3 A3: Stratified Asset-Pool Construction

Hotel pools are stratified by hotel level and constrained by geographic
concentration. Flight pools are stratified by distance band and constrained by
carrier concentration. The current sampler uses a minimum allocation per stratum,
so the realized pool size can differ from the target size; the manuscript must
report the realized size rather than only the requested size.

### 4.4 A4: Time-Differentiated Issuance

Issuance uses separate price bands for holidays, weekends, and weekdays. The
issuance quantity is:

```text
quantity = rooms_or_seats * days * oversubscription_multiplier
```

---

## 5. Machine-Learning Probability of Default

### 5.1 Learning Task

For hotel `i` observed in month `t`, the model predicts whether the hotel is absent
from the platform panel in month `t + 3`. This target is called platform exit. It
is a measurable proxy, not a verified legal default.

### 5.2 Data and Cohorts

The hotel panel contains 1,707,918 hotel-day records and 16,257 hotels from March
to June 2024 in Chengdu. The main cohort contains 14,851 hotels with a 7.84% exit
rate. Rolling cohorts are used as a stability check.

### 5.3 Features

Features are computed only from the observation month:

| Group | Features |
|---|---|
| Price level | Mean, median, minimum, maximum |
| Volatility | Log-return standard deviation, annualized volatility, range ratio |
| Trend | Monthly change, slope, momentum |
| Shape | Day-of-week pattern, within-month variation, residual seasonality |
| Completeness | Record count, days present, observation span |
| Structure | Hotel level, district, longitude, latitude |
| Competition | Same-district and same-level hotel count |

Completeness is the strongest single group and is also a known confounder. We
therefore report ablations with and without completeness and compare a price-only
model.

### 5.4 Models and Baselines

The main models are random forest and LightGBM, with logistic regression as a
statistical baseline and a GRU as a sequence-model extension. Merton and KMV are
structural baselines on the dense-history subsample.

### 5.5 Evaluation

We report AUC and PR-AUC for discrimination, and Brier score, expected calibration
error, and reliability diagrams for calibration. The downstream experiment feeds
each calibrated PD vector into the same cash-flow waterfall.

### 5.6 Preliminary Results

| Cohort | N | Exit rate | AUC | PR-AUC |
|---|---:|---:|---:|---:|
| 2024-03 -> 2024-06 | 14,851 | 7.84% | 0.8290 | 0.3843 |
| 2024-03 -> 2024-05 | 14,851 | 6.90% | 0.8675 | 0.4125 |
| 2024-04 -> 2024-06 | 15,710 | 6.29% | 0.8956 | 0.5623 |

The price-only model reaches AUC 0.7474, while the best economic single feature,
mean price, reaches 0.6522. On the dense-history subsample, Merton reaches AUC
0.5644 and KMV reaches 0.6270. These subsample results are not directly comparable
to the full-cohort results because the positive rate falls from 7.84% to 2.10%.

The calibration experiment provides the central downstream result. Across seven
configurations, the AUC range is 0.0355 while the ECE range is 0.3050. Balanced
class weights can leave ranking nearly unchanged but inflate mean predicted PD;
isotonic calibration restores the probability level.

---

## 6. Experiments and Simulation

### 6.1 System Performance

`[TODO: Report end-to-end runtime, module-level runtime, and parallel speedup.
The three nested Python loops in the time-right market simulation are a candidate
optimization target.]`

### 6.2 Monte Carlo and Tranche Losses

`[TODO: Add the hotel and flight Monte Carlo loss distributions, VaR, expected
loss, and tranche ratings from the finalized engine.]`

The flight pool reported in the method record contains 69 routes and 11 carriers.
The senior tranche has expected loss near zero and an Aaa-Aa rating, while the
maximum pool loss is 15.6%, below the 35% subordination protection.

### 6.3 Downstream Effect of PD Calibration

`[TODO: Feed all calibrated PD vectors into the same waterfall and report how
senior, mezzanine, junior, and equity losses and ratings change.]`

### 6.4 Ablations

The planned ablations are:

- Remove copula tail dependence.
- Replace the ML PD component with the structural baseline.
- Change the exit-to-default mapping.
- Compare full features, no-completeness, and price-only models.

---

## 7. Discussion and Limitations

The study has three primary limitations. First, the four-month hotel panel cannot
support a true temporal out-of-sample test across seasonal or credit cycles.
Second, platform exit is not the same event as default; the exit-to-default
mapping remains a sensitivity assumption. Third, the current prototype is an
offline simulator, not a deployed on-chain system.

The structural-model comparison is also limited by coverage. The models require
dense price histories, and the eligible subsample is safer than the full cohort.
The correct conclusion is that the structural inputs are weakly informative in
this setting, not that structural models fail universally.

---

## 8. Conclusion

`[TODO: Rewrite after the P1 experiments and tranche results are frozen.]`

FSR securitization couples a service-market mechanism with a credit-risk engine.
The present work turns that coupling into an executable simulation system and
shows why probability calibration must be evaluated alongside discrimination.
The next step is to freeze the feature pipeline, complete the downstream tranche
experiments, and convert this working draft into a submission-ready manuscript.

---

## Data and Code Availability

The hotel price panel, flight aggregates, data dictionary, reference material, and
P0 scripts are included in this repository. Raw DB1B archives are downloaded on
demand and are not committed. The original structural-model scripts referenced by
the P0 experiments remain outside this repository and must be migrated before the
full experiment can be reproduced from a clean checkout.

## References

`[TODO: Create paper/references.bib and map the PDFs under papers/ to citation
keys. Do not submit this section until every DOI and venue is verified.]`
