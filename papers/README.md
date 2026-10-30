# 参考文献库

本目录收集论文所需文献。优先收录**开放获取（OA）**的 PDF；付费墙文献不绕过，
集中列在 [`TO_DOWNLOAD.md`](TO_DOWNLOAD.md) 由人工获取。

> 版权提示：这些 PDF 版权归原作者与出版方所有，仅供研究阅读；
> 本仓库的 MIT 许可**不覆盖** `papers/` 下的 PDF。引用请以正式出版版本为准。

**当前：已收录 17 篇（2021–2023 共 8 篇，2024–2026 共 9 篇）。**

另有 **25 条经 DOI/OpenAlex 核验的核心文献元数据**，见
[`hotel_flight_fsr.bib`](hotel_flight_fsr.bib)。同一组条目已导入 Zotero 的
**我的文库 → 酒店与机票 FSR** 分类；订阅制、无公开版本的条目只保留规范元数据和
DOI，不绕过出版方权限。

---

## 一、2024–2026（近期，9 篇）

| 文件 | 标题 | 来源 | 年份 |
|---|---|---|---|
| `2024_rf_overfitting_probability.pdf` | Understanding overfitting in random forest for probability estimation: a visualization and simulation study | Diagnostic and Prognostic Research | 2024 |
| `2024_rl_aviation_survey.pdf` | A Survey on Reinforcement Learning in Aviation Applications | Engineering Applications of AI | 2024 |
| `2024_appointment_overbooking_ml.pdf` | Smart Medical Appointment Scheduling: Optimization, Machine Learning and Overbooking to Enhance Resource Utilization | IEEE Access | 2024 |
| `2024_rm_without_forecasting.pdf` | Revenue Management without Demand Forecasting: A Data-Driven Approach for Bid Price Generation | J. Revenue and Pricing Management | 2024 |
| `2024_booking_trends_ai.pdf` | Prediction of Booking Trends and Customer Demand in the Tourism and Hospitality Sector Using AI-Based Models | IJACSA | 2024 |
| `2024_climate_risk_securitization.pdf` | Adaptation Using Financial Markets: Climate Risk Diversification through Securitization | NBER Working Paper w32244 | 2024 |
| `2025_calibration_distribution_shift.pdf` | Evaluating calibration of deep fault diagnostic models under distribution shift | Computers in Industry | 2025 |
| `2025_rl_vs_dp_dynamic_pricing.pdf` | Reinforcement learning versus data-driven dynamic programming: a comparison for finite horizon dynamic pricing markets | J. Revenue and Pricing Management | 2025 |
| `2025_air_cargo_dynamic_pricing.pdf` | Dynamic Pricing for Air Cargo Revenue Management | Transportation Research Part E | 2025 |

## 二、2021–2023（基础文献，8 篇）

| 文件 | 标题 | 来源 | 年份 |
|---|---|---|---|
| `2021_credit_scoring_logistic_tree.pdf` | Machine learning for credit scoring: Improving logistic regression with non-linear decision-tree effects | European Journal of Operational Research | 2021 |
| `2021_mbs_returns_cross_section.pdf` | The Cross Section of MBS Returns | The Journal of Finance | 2021 |
| `2022_corporate_credit_dnn_l1l2.pdf` | Deep neural networks with L1 and L2 regularization for high dimensional corporate credit risk prediction | Expert Systems with Applications | 2022 |
| `2022_credit_default_ml_model_risk.pdf` | Measuring the model risk-adjusted performance of machine learning algorithms in credit default prediction | Financial Innovation | 2022 |
| `2022_online_learning_pricing_service.pdf` | Online Learning and Pricing for Service Systems with Reusable Resources | Operations Research | 2022 |
| `2023_classifier_calibration_survey.pdf` | Classifier calibration: a survey on how to assess and improve predicted class probabilities | Machine Learning | 2023 |
| `2023_defi_nft_digital_assets.pdf` | Value creation and capture in decentralized finance markets: Non-fungible tokens as a class of digital assets | Electronic Markets | 2023 |
| `2023_interpretable_ml_credit_scoring.pdf` | Interpretable machine learning for imbalanced credit scoring datasets | European Journal of Operational Research | 2024 |

---

## 三、主题索引

| 主题 | 已收录 |
|---|---|
| 信用风险 / 机器学习 PD | `2021_credit_scoring_logistic_tree`、`2022_corporate_credit_dnn_l1l2`、`2022_credit_default_ml_model_risk`、`2023_interpretable_ml_credit_scoring` |
| 概率校准 / 类别不平衡 | `2023_classifier_calibration_survey`、`2024_rf_overfitting_probability`、`2025_calibration_distribution_shift` |
| 证券化 / 代币化 / 区块链金融 | `2021_mbs_returns_cross_section`、`2023_defi_nft_digital_assets`、`2024_climate_risk_securitization` |
| 酒店 / 旅游运营 | `2024_booking_trends_ai` |
| 航空 / 收益管理 / 动态定价 | `2024_rl_aviation_survey`、`2024_rm_without_forecasting`、`2025_rl_vs_dp_dynamic_pricing`、`2025_air_cargo_dynamic_pricing` |
| 容量约束与超售 | `2024_appointment_overbooking_ml`、`2022_online_learning_pricing_service` |

---

## 四、Zotero 与规范书目

- Zotero 分类：`我的文库 → 酒店与机票 FSR`
- 顶层文献记录：25 条
- 带 PDF 附件：8 条
- 可复现书目：`papers/hotel_flight_fsr.bib`
- 元数据核验日期：2026-10-30
- 核验来源：Crossref；预印本 *Miles as Capital* 使用 OpenAlex 核对作者和年份

重新导入时，在 Zotero 中选中该分类，再通过连接器导入上述 BibTeX 文件。
没有公开 PDF 的订阅制文章需从机构渠道人工补附件。

---

## 五、检索方法（可复现）

- 来源：OpenAlex（`title_and_abstract.search`，限定开放获取与起始年份）、
  Semantic Scholar、arXiv；2024–2026 部分单独按 `from_publication_date:2024-01-01` 检索。
- 说明：第一轮按引用量降序，天然偏向 2021–2023 的老论文；因此又单独补了 2024 年之后的批次，
  使近期文献占比过半。
- 开放版本定位：OpenAlex `best_oa_location.pdf_url`、机构仓库、arXiv、NBER 等公开渠道。
- MDPI、Wiley、Elsevier 的部分 PDF 有反爬保护，未能自动下载，已列入 `TO_DOWNLOAD.md`。
