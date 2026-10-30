# 未来服务权的证券化研究：酒店客房夜与航空座位

> 这是一个论文研究与写作仓库，不只是数据包。项目研究未来服务权
> （Future Service Rights, FSR）如何被证券化、定价和评估风险，并把酒店客房夜与
> 航空座位放在同一个仿真框架下比较。

**工作题目**

> *A Simulation System for Future Service Rights Securitization:
> Architecture, Algorithms, and Machine-Learning Credit Assessment*

**论文主张**：FSR 证券化需要可靠的概率违约估计。传统结构式模型在稀疏的酒店
借款人数据上缺少可观测输入，因此本文构建一个可执行的证券化仿真系统，用真实价格
面板训练 PD 代理模型，并证明概率校准而非单纯排序能力决定下游分层风险。

## 当前状态

| 阶段 | 状态 | 说明 |
|---|---|---|
| P0 可行性预实验 | 已完成 | 三队列 AUC 0.8290 到 0.8956，ML PD 路线成立 |
| P1 数据与特征工程 | 待启动 | 需要冻结特征、队列和验证协议 |
| 论文骨架 | 已建立 | 英文工作稿位于 `paper/manuscript.md` |
| 仿真实验 | 部分完成 | 机票池已有结果，酒店瀑布与下游评级待补 |
| 投稿目标 | 待定 | 当前按 CS/EI 9 到 10 页仿真系统论文设计 |

## 从这里开始

| 入口 | 内容 |
|---|---|
| [论文工作稿](paper/manuscript.md) | 当前正文、摘要、实验表和待补位置 |
| [论文写作看板](paper/README.md) | 贡献台账、章节状态、证据登记和下一步 |
| [当前方法](docs/PAPER_METHODS.md) | 系统架构、A1 到 A4 算法、PD 建模和机票扩展 |
| [旧方法档案](docs/OLD_METHODS.md) | 机制设计旧稿、Merton/KMV 基线及失效原因 |
| [改稿方案](docs/reference/REVISION_PLAN.md) | 从 24 页机制设计稿转向 10 页系统论文 |
| [图表计划](paper/figures/README.md) | 主图、表格和证据来源 |
| [数据字典](DATA_DICTIONARY.md) | 字段、规模、SHA-256 与数据来源 |

## 三条贡献

1. **系统与算法**：FSR 证券化仿真器，包含 copula 相依违约抽样、
   OC/IC 现金流瀑布、资产池分层抽样和并行蒙特卡洛。
2. **机器学习 PD**：把酒店平台退出重构为面板分类任务，替代在稀疏借款人上
   输入近乎无信息的 Merton/KMV 主模型。
3. **校准重于判别**：在判别力接近的模型中，概率校准差异会显著改变分层预期损失
   和评级。

## 方法演进

旧方法并非完全废弃。项目保留 FSR 定义、分层结构、copula、现金流瀑布和压力测试，
但不再把"提出新资产类别"作为论文主贡献，也不再让 Merton/KMV 承担核心 PD 估计。

| | 旧方法 | 当前方法 |
|---|---|---|
| 论文定位 | FSR 机制设计与新资产类别 | 证券化仿真系统与算法 |
| 信用模型 | Merton DD + GARCH、KMV | 价格面板特征 + 逻辑回归 / 树模型 / GRU |
| 预测对象 | 结构式违约概率 | 平台退出代理标签，再做 PD 映射与敏感性分析 |
| 评估重点 | PD 水平和排序 | AUC、PR-AUC、Brier、ECE 和可靠性图 |
| 结构式模型角色 | 核心方法 | 对照基线 |

旧模型在原始资产池中使 65/66 家酒店触及 50% PD 上限；P0 子样本中 Merton 的
AUC 为 0.5644，全队列年化波动率的 AUC 仅为 0.5076。完整记录见
[旧方法档案](docs/OLD_METHODS.md)。

## 仓库结构

```text
paper/           论文正文、写作看板、图表计划
docs/            当前方法、旧方法档案、改稿方案和 P0 实验脚本
data/            酒店价格面板、机票聚合结果和溯源脚本
papers/          参考文献、规范 BibTeX 与待下载清单
scripts/         DB1B 原始数据下载与校验
```

## 数据与实验

### 酒店

- 16,257 家酒店，1,707,918 条酒店日价格记录，窗口为 2024-03-01 至 2024-06-30。
- 2024-03 队列包含 14,851 家酒店，三个月退出率为 7.84%。
- 价格单位为分；中位数 16,700 表示每晚 167 元。
- 元数据覆盖 86,159 家酒店，可构造档位、位置和本地竞争特征。

### 机票

- 美国交通部 DB1B 起讫点调查，覆盖 13 个季度和 25 家航司。
- 仓库保存航线级聚合数据、EDA 汇总、航司相关阵和 FSR 结果。
- 原始 DB1B 压缩包按需下载，不提交到 Git。

完整字段、文件规模和校验和见 [DATA_DICTIONARY.md](DATA_DICTIONARY.md)。

## 复现

下载并校验 DB1B：

```bash
python scripts/download_db1b.py --unzip
```

P0 实验脚本位于 `docs/reference/`。它们引用了原始工作树中的
`config.py`、`credit_model.py` 和 `robustness_checks.py`，当前不能从干净克隆
直接运行；迁移这些依赖是下一阶段任务。

从原始 DB1B 重建航线聚合：

```bash
python data/provenance/extract_real_routes.py
```

## 写作流程

1. 先改 `paper/manuscript.md`，正文是唯一主稿。
2. 新结论或新数字同步登记到 `paper/README.md` 的证据台账。
3. 方法变化写入 `docs/PAPER_METHODS.md`，被替换的路线写入
   `docs/OLD_METHODS.md`。
4. 图件按 `paper/figures/README.md` 的编号和来源生成。
5. 提交前检查所有 `[TODO: ...]`、引用、样本口径和限制说明。

## 数据来源与许可

酒店数据取自 `hotel-order-financialization` 本地工作树提交 `4be93ae`，
酒店 CSV 为逐字节复制。`papers/` 下 PDF 的版权归原作者和出版方所有，
不适用仓库的 MIT 许可。

代码与原创文档采用 MIT 许可，见 [LICENSE](LICENSE)。
