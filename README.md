# 酒店 & 机票 未来服务权（FSR）—— 研究数据

本仓库是一篇论文的**数据包**：把 **未来服务权（Future Service Rights, FSR）**
框架同时应用到**酒店客房夜**与**航空座位**两个市场。

FSR 是对**一份未来易逝服务产能**的凭证化索取权。酒店客房夜和航班座位是它最典型
的两个实例，因此放在一起研究。

仓库包含两部分：**分析就绪的数据表**（以及获取原始数据所需的代码），
和 `docs/` 下记录论文**所用方法**的文档。仿真引擎与论文正文在此数据包之上构建。

## 仓库结构

```
data/           分析就绪的数据集（见下方清单）
scripts/        download_db1b.py —— 下载并校验 DB1B 原始季度文件
docs/           PAPER_METHODS.md + 论文参考文献材料
```

---

## 数据清单

| 路径 | 大小 | 行数 | 内容 |
|---|---:|---:|---|
| `data/hotel/cleaned_hotel_prices.csv` | 51.3 MB | 1,707,918 | 清洗后的日价格面板：`date`、`hotelCode`、`price`（价格单位为**分**） |
| `data/hotel/2024_3.csv` … `2024_6.csv` | 每个约 13.8 MB | 每个约 43 万行 | 原始日价格，2024 年 3–6 月（清洗面板的来源） |
| `data/hotel/hotel_info.csv` | 6.3 MB | 86,159 | 酒店元数据：`hotelName`、`hotelLevel`、`lon经度`、`lat纬度` |
| `data/hotel/hotel_future_prices.csv` | 0.3 MB | 16,257 | 每家酒店的派生远期价：`hotelCode`、`futurePrice` |
| `data/flight/flight_routes_real.csv` | 2.1 MB | 25,872 | 来自 DB1B 2024Q2 的航线级统计：`mean_fare`、`std_fare`、`fare_cv`、`n_carriers`、距离档、航司列表 |
| `data/flight/flight_eda_v4_summary.json` | 7 KB | — | 全量 DB1B EDA 汇总：13 个季度（2022Q1–2025Q1）、9,734 万行、102,279 条航线、25 家航司 |
| `data/flight/empirical_carrier_correlations.json` | 2 KB | — | 9 家航司权益收益相关阵（5 年日频，2021–2025） |
| `data/flight/flight_fsr_results_v1.json` | 55 KB | — | 机票 FSR 引擎输出（蒙特卡洛 / 分层结果） |
| `data/flight/db1b_manifest.json` | 2 KB | — | 13 个 DB1B 季度：文件名、URL、字节大小 |
| `data/provenance/*.py` | — | — | 生成机票聚合数据的脚本（保留以溯源） |

逐字段说明与 SHA-256 校验和见 [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)。

---

## 酒店数据

- 覆盖范围：**16,257 家酒店**，日价格窗口 **2024-03-01 至 2024-06-30**（中国成都）。
- 仅 2024-03 一个月就有 **14,851** 家酒店——即生存 / 平台退出分析所用的队列规模。
- 价格单位为**分**（1 元 = 100 分）；中位数 16,700 = 每晚 167 元。
- `hotelLevel` 取四个值：`经济` / `舒适` / `高档` / `豪华`。

该面板可支撑：价格水平、波动率、趋势与季节性特征；平台退出标签（某酒店在后续月份的
面板中消失）；以及本地竞争密度（按区县与档位统计酒店数，来自 86,159 行元数据）。

## 机票数据

原始来源是美国交通部（U.S. DOT）**DB1B** 起讫点调查（Market），为全美国内机票的
10% 季度抽样。数据公开：<https://www.transtats.bts.gov/>

> **DB1B 原始压缩包不存放在本仓库中。** 每个约 78–105 MB，13 个季度合计约 1.27 GB，
> 其中三个超过 GitHub 单文件 100 MiB 的上限。请用以下命令下载并校验：
>
> ```bash
> python scripts/download_db1b.py --unzip
> ```
>
> 下载支持断点续传，并按 `data/flight/db1b_manifest.json` 中的字节数逐个校验。
> 若要从原始压缩包重建 `flight_routes_real.csv`，运行
> `data/provenance/extract_real_routes.py`。

机票 EDA 的关键事实：9,734 万条票价记录、102,279 条起讫点航线、25 家航司、
平均票价变异系数（fare CV）约 0.56。

---

## 数据来源

取自 `hotel-order-financialization`
（`https://github.com/David-coder-hnu/hotel-order-financialization`）本地工作树，
提交 `4be93ae`。酒店 CSV 为逐字节复制，所有 SHA-256 校验和记录在
`DATA_DICTIONARY.md` 中。

## 许可

MIT —— 见 [`LICENSE`](LICENSE)。
