# Reference coverage

This file maps the manuscript's main topics to anchor references in
[`references.bib`](references.bib). It records citation coverage, not empirical
evidence. Search and DOI verification were performed on 2026-11-27.

The library contains 71 unique records: 64 DOI-bearing works and 7 historical or
official sources without DOI. Seventeen records link to local PDFs under
`papers/`, and the current manuscript cites 44 of the 71 records. Every citation
key used in the manuscript resolves to an entry in `references.bib`.

| Manuscript topic | Anchor references | Coverage |
|---|---|---|
| Structural credit models | `merton1974pricing`, `kealhofer2003quantifying`, `bharath2008forecasting` | Primary model and empirical validation |
| Machine-learning default prediction | `dumitrescu2022creditscoring`, `yang2023creditdnn`, `chen2024imbalanced`, `benjabeur2023xgboost`, `elhoseny2025distress`, `alonso2022modelrisk`, `aruleba2024ensemblecredit`, `liu2024causalcredit`, `chang2024creditcard` | Statistical and deep baselines plus model-risk and interpretability studies |
| Probability calibration | `brier1950verification`, `platt1999probabilistic`, `zadrozny2002transforming`, `niculescu2005predicting`, `guo2017calibration`, `silvafilho2023calibration`, `piccininni2024resampling`, `barrenada2024rfcalibration`, `xiao2025calibrationshift` | Original methods, surveys, imbalance corrections and distribution shift |
| Copula-based dependence | `li2000defaultcorrelation`, `wang2024cleanenergycopula`, `nguyen2024factorcopula`, `zhang2024defaultdependence` | Default correlation and financial dependence modelling |
| Overbooking and revenue management | `beckmann1958decision`, `rothstein1971airlineoverbooking`, `littlewood1972forecasting`, `talluri2004theory`, `pimentel2019hoteloverbooking`, `schwartz2025hoteloverbooking` | Airline foundations, hotel applications and the revenue-management synthesis |
| Frequent-flyer-backed finance | `berglund2025miles`, `deboer2018standalone`, `gao2020valuingmiles`, `american2021aadvantage`, `delta2015skymiles`, `united2013mileageplus` | Academic interpretation plus SEC evidence of collateral, prepayments and partner cash flows |
| Securitization and tokenized assets | `diep2021mbs`, `schaer2021defi`, `schwiderowski2023nft`, `kreppmeier2023securitytokens`, `zhang2021expresswayabs`, `kumar2024blockchainabs`, `latino2025greenabs`, `kahn2024climateabs` | MBS, ABS, tokenization and real-world asset precedents |
| Hotel demand and hospitality risk | `viverit2023hotelbooking`, `contessi2024hoteloccupancy`, `rekiek2024bookingtrends`, `henriques2024hotelreview`, `crespi2021hospitalitydistress`, `guillet2021hotelrevenue`, `boto2022domestictourism` | Forecasting, revenue management and distress context |
| Airline competition and pricing | `fukushi2022chairs`, `sun2024airlinecompetition`, `gaggero2023hiddencity`, `bulbul2025airfare`, `fageda2024servicequality`, `eren2024revenue`, `lange2025rlvsdp`, `du2025aircargo` | Simulation, competition, fare prediction and dynamic pricing |
| Service-system learning | `jia2024onlinelearning`, `razzaghi2024rlaviation`, `valenzuela2024overbooking` | Online pricing, reinforcement learning and overbooking under reusable capacity |

## Remaining evidence gaps

- The repository does not contain the final hotel Monte Carlo, waterfall, or
  downstream tranche results.
- The structural-model scripts required to reproduce the Merton/KMV comparisons
  are not yet imported into the repository.
- The four-month hotel panel does not support a true temporal out-of-sample test.
- Platform exit remains a proxy for default.

These are experimental and reproducibility gaps. They do not indicate missing
bibliographic coverage for the claims currently written in the manuscript.
