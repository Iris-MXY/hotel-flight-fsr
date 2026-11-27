# 文献覆盖审计

本文件把论文的主要主题映射到 [`references.bib`](references.bib) 中的锚点文献。
它记录的是引用覆盖情况，而不是实验证据。检索与 DOI 核验日期为 2026-11-27。

文献库包含 71 条唯一记录，其中 64 条带 DOI，7 条为无 DOI 的经典文献或官方文件。
17 条记录关联到 `papers/` 下的本地 PDF；当前正文引用 44 条文献。正文使用的每个
引用键都能在 `references.bib` 中找到对应条目。

| 论文主题 | 锚点文献 | 覆盖情况 |
|---|---|---|
| 结构式信用模型 | `merton1974pricing`、`kealhofer2003quantifying`、`bharath2008forecasting` | 原始模型与样本外验证 |
| 机器学习违约预测 | `dumitrescu2022creditscoring`、`yang2023creditdnn`、`chen2024imbalanced`、`benjabeur2023xgboost`、`elhoseny2025distress`、`alonso2022modelrisk`、`aruleba2024ensemblecredit`、`liu2024causalcredit`、`chang2024creditcard` | 统计基线、深度基线、模型风险与可解释性 |
| 概率校准 | `brier1950verification`、`platt1999probabilistic`、`zadrozny2002transforming`、`niculescu2005predicting`、`guo2017calibration`、`silvafilho2023calibration`、`piccininni2024resampling`、`barrenada2024rfcalibration`、`xiao2025calibrationshift` | 原始方法、综述、类别重采样与分布漂移 |
| copula 依赖结构 | `li2000defaultcorrelation`、`wang2024cleanenergycopula`、`nguyen2024factorcopula`、`zhang2024defaultdependence` | 违约相关性与金融相依建模 |
| 超售与收益管理 | `beckmann1958decision`、`rothstein1971airlineoverbooking`、`littlewood1972forecasting`、`talluri2004theory`、`pimentel2019hoteloverbooking`、`schwartz2025hoteloverbooking` | 航空基础模型、酒店应用与收益管理综合文献 |
| 常旅客计划融资 | `berglund2025miles`、`deboer2018standalone`、`gao2020valuingmiles`、`american2021aadvantage`、`delta2015skymiles`、`united2013mileageplus` | 学术解释，以及 SEC 文件中的质押、预付款和合作方现金流证据 |
| 证券化与代币化资产 | `diep2021mbs`、`schaer2021defi`、`schwiderowski2023nft`、`kreppmeier2023securitytokens`、`zhang2021expresswayabs`、`kumar2024blockchainabs`、`latino2025greenabs`、`kahn2024climateabs` | MBS、ABS、代币化与真实世界资产先例 |
| 酒店需求与行业风险 | `viverit2023hotelbooking`、`contessi2024hoteloccupancy`、`rekiek2024bookingtrends`、`henriques2024hotelreview`、`crespi2021hospitalitydistress`、`guillet2021hotelrevenue`、`boto2022domestictourism` | 需求预测、收益管理与经营困境背景 |
| 航空竞争与定价 | `fukushi2022chairs`、`sun2024airlinecompetition`、`gaggero2023hiddencity`、`bulbul2025airfare`、`fageda2024servicequality`、`eren2024revenue`、`lange2025rlvsdp`、`du2025aircargo` | 仿真、竞争、票价预测与动态定价 |
| 服务系统学习 | `jia2024onlinelearning`、`razzaghi2024rlaviation`、`valenzuela2024overbooking` | 在线定价、强化学习与可复用产能超售 |

## 仍需补充的证据

- 仓库尚未汇总最终版酒店蒙特卡洛、现金流瀑布和下游分层结果。
- 用于复现 Merton/KMV 比较的结构式模型脚本尚未迁入仓库。
- 四个月的酒店面板无法支持真正的时间外样本检验。
- “平台退出”仍然只是违约的代理指标。

这些缺口属于实验证据与可复现性缺口，不表示当前论文主张缺少文献覆盖。
