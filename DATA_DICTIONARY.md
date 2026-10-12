# 数据字典

酒店数据均为带表头的 UTF-8 CSV 文件；机票聚合数据使用下述模式。
SHA-256 校验和列于文末。

---

## 酒店

### `data/hotel/cleaned_hotel_prices.csv`

清洗后的日价格面板——构建特征与标签的主表。

| 列名 | 类型 | 说明 |
|---|---|---|
| `date` | 字符串 | `YYYY/M/D`，范围 2024-03-01 … 2024-06-30 |
| `hotelCode` | 字符串 | 酒店编号，例如 `H00003179890` |
| `price` | 浮点 | 每晚房价，单位**分**（1 元 = 100 分） |

行数：1,707,918 · 酒店数：16,257

### `data/hotel/2024_3.csv` … `2024_6.csv`

原始日价格，每月一个文件。列为 `date` / `hotelCode` / `price`，另有若干空列。
用于重新生成清洗面板或审计清洗规则。

### `data/hotel/hotel_info.csv`

酒店元数据，用于竞争密度与位置特征。

| 列名 | 类型 | 说明 |
|---|---|---|
| `hotelCode` | 字符串 | 与价格面板的连接键 |
| `hotelName` | 字符串 | 酒店名称 |
| `hotelLevel` | 字符串 | `经济` / `舒适` / `高档` / `豪华` |
| `lon经度` | 浮点 | 经度 |
| `lat纬度` | 浮点 | 纬度 |

行数：86,159（全城名录，比有价格记录的 16,257 家更广）

### `data/hotel/hotel_future_prices.csv`

每家酒店的派生远期价。

| 列名 | 类型 | 说明 |
|---|---|---|
| `hotelCode` | 字符串 | 酒店编号 |
| `futurePrice` | 浮点 | 远期价，单位分（派生量） |

行数：16,257

---

## 机票

### `data/flight/flight_routes_real.csv`

由 DB1B 2024Q2 聚合得到的航线级统计（观测数 ≥ 20 的航线）。

| 列名 | 说明 |
|---|---|
| `origin`、`dest`、`route` | 起讫机场代码及 `origin-dest` 标签 |
| `n_obs` | 该航线的机票观测数 |
| `total_pax` | 抽样乘客数之和 |
| `mean_fare`、`std_fare` | 票价水平与离散度（美元） |
| `fare_cv` | `std_fare / mean_fare` |
| `n_carriers` | 不同申报航司数 |
| `avg_distance`、`avg_coupons` | 平均飞行英里数与航段数 |
| `dist_band` | `short` / `medium` / `long` |
| `carriers_list` | 逗号分隔的航司代码 |

行数：25,872

### `data/flight/flight_eda_v4_summary.json`

覆盖 DB1B 全时间段（2022Q1–2025Q1）的聚合 EDA：数据集总量、全局票价统计、
集中度（航司 HHI、前四份额）、航线波动率统计、分航司风险表、分季度行数 / 票价。

### `data/flight/empirical_carrier_correlations.json`

航司权益收益相关阵（9 家航司，5 年日对数收益，2021–2025，1,192 个交易日），
用于机票池的相依结构。

### `data/flight/flight_fsr_results_v1.json`

机票 FSR 引擎输出（蒙特卡洛路径、分层损失、压力与敏感性结果）。

### `data/flight/db1b_manifest.json`

13 个 DB1B 季度的清单：季度、文件名、下载 URL、字节大小，以及总计。

### `data/provenance/*.py`

生成机票聚合数据的脚本（`extract_real_routes.py`、`flight_eda_v4.py`、
`eda_12q_panel.py`、`eda_flight_full.py`）。它们引用了本仓库之外的 DB1B 目录；
重建时请先修改该路径。

---

## SHA-256 校验和

| 文件 | SHA-256 |
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
