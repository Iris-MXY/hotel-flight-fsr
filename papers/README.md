# 参考文献库

本目录收集论文所需的文献。优先收录 **开放获取（OA）** 的 PDF，
按主题分为「信用风险与机器学习 PD / 概率校准 / 证券化与代币化 /
酒店与旅游运营 / 航空运营 / copula 依赖结构」。

> 说明：本目录中的 PDF 版权归原作者与出版方所有，仅用于研究阅读；
> 本仓库的 MIT 许可**不覆盖**这些 PDF。引用请以正式出版版本为准。

---

## 一、已下载（6 篇，开放获取）

| 文件 | 标题 | 期刊 / 会议 | 年份 | 引用 |
|---|---|---|---|---|
| `2023_classifier_calibration_survey.pdf` | Classifier calibration: a survey on how to assess and improve predicted class probabilities | Machine Learning | 2023 | 209 |
| `2022_credit_default_ml_model_risk.pdf` | Measuring the model risk-adjusted performance of machine learning algorithms in credit default prediction | Financial Innovation | 2022 | 79 |
| `2022_corporate_credit_dnn_l1l2.pdf` | Deep neural networks with L1 and L2 regularization for high dimensional corporate credit risk prediction | Expert Systems with Applications | 2022 | 95 |
| `2021_mbs_returns_cross_section.pdf` | The Cross Section of MBS Returns | The Journal of Finance | 2021 | 44 |
| `2023_defi_nft_digital_assets.pdf` | Value creation and capture in decentralized finance markets: Non-fungible tokens as a class of digital assets | Electronic Markets | 2023 | 47 |
| `2022_online_learning_pricing_service.pdf` | Online Learning and Pricing for Service Systems with Reusable Resources | Operations Research | 2022 | 31 |

---

## 二、待下载（19 篇，需要机构订阅或手动获取）

按主题排列。DOI 可直接解析到正式页面；标 ★ 的是与本文最相关、优先级最高的。

### 信用风险与机器学习 PD

| 标题 | 期刊 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ Machine learning for credit scoring: Improving logistic regression with non-linear decision-tree effects | European Journal of Operational Research | 2021 | 433 | `10.1016/j.ejor.2021.06.053` |
| ★ Interpretable machine learning for imbalanced credit scoring datasets | European Journal of Operational Research | 2023 | 182 | `10.1016/j.ejor.2023.06.036` |
| Bankruptcy Prediction using the XGBoost Algorithm and Variable Importance Feature Engineering | Computational Economics | 2022 | 200 | `10.1007/s10614-021-10227-1` |
| Deep Learning-Based Model for Financial Distress Prediction | Annals of Operations Research | 2022 | 122 | `10.1007/s10479-022-04766-5` |

### 概率校准与类别不平衡

| 标题 | 期刊 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ The harm of class imbalance corrections for risk prediction models: illustration and simulation using logistic regression | JAMIA | 2022 | 363 | `10.1093/jamia/ocac093` |
| ★ Dynamically Weighted Balanced Loss: Class Imbalanced Learning and Confidence Calibration of Deep Neural Networks | IEEE TNNLS | 2021 | 334 | `10.1109/tnnls.2020.3047335` |

### 证券化与代币化

| 标题 | 期刊 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ Real estate security token offerings and the secondary market: Driven by crypto hype or fundamentals? | Journal of Banking & Finance | 2023 | 67 | `10.1016/j.jbankfin.2023.106940` |
| ★ Sustainable Construction and Financing—Asset-Backed Securitization of Expressway's Usufruct with Redeemable Rights | Sustainability | 2021 | 6 | `10.3390/su13169113` |
| Decentralized Finance: On Blockchain- and Smart Contract-Based Financial Markets | Federal Reserve Bank of St. Louis Review | 2021 | 591 | `10.20955/r.103.153-74` |

### 酒店与旅游运营

| 标题 | 期刊 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ Application of machine learning to cluster hotel booking curves for hotel demand forecasting | Int. Journal of Hospitality Management | 2023 | 58 | `10.1016/j.ijhm.2023.103455` |
| ★ Financial distress in the hospitality industry during the Covid-19 disaster | Tourism Management | 2021 | 151 | `10.1016/j.tourman.2021.104301` |
| Managing hotel revenue amid the COVID-19 crisis | Int. Journal of Contemporary Hospitality Mgmt | 2021 | 87 | `10.1108/ijchm-06-2020-0623` |
| Domestic tourism and the resilience of hotel demand | Annals of Tourism Research | 2022 | 70 | `10.1016/j.annals.2022.103352` |

### 航空运营与竞争

| 标题 | 期刊 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ CHAIRS: A choice-based air transport simulator applied to airline competition and revenue management | Transportation Research Part A | 2021 | 12 | `10.1016/j.tra.2021.11.010` |
| Airline competition: A comprehensive review of recent research | J. of the Air Transport Research Society | 2024 | 52 | `10.1016/j.jatrs.2024.100013` |
| The determinants of hidden-city ticketing: Competition, hub-and-spoke networks, and advance-purchase requirements | Transportation Research Part E | 2023 | 12 | `10.1016/j.tre.2023.103086` |

### copula 依赖结构

| 标题 | 期刊 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ Measuring the Systemic Risk of Clean Energy Markets Based on the Dynamic Factor Copula Model | Systems | 2024 | 2 | `10.3390/systems12120584` |
| Default dependence in the insurance and banking sectors: A copula approach | J. of Int. Financial Markets, Institutions & Money | 2023 | 2 | `10.1016/j.intfin.2023.101911` |

### 常旅客计划（FSR 的产业先例）

| 标题 | 来源 | 年份 | 引用 | DOI |
|---|---|---|---|---|
| ★ Miles as Capital: How Frequent Flyer Programs sustained North American Airlines During COVID-19 | Preprint | 2025 | 0 | `10.13140/rg.2.2.32889.43360` |

---

## 三、检索方法（可复现）

- 来源：OpenAlex（`title_and_abstract.search`，限定 `from_publication_date:2021-01-01`、
  开放获取、按 `cited_by_count` 降序）与 Semantic Scholar（相关性排序）。
- 开放版本定位：OpenAlex `best_oa_location.pdf_url`，Unpaywall 作为备选。
- 只下载出版方或作者仓库公开提供的 PDF；付费墙文献不绕过，列入上表由人工获取。
