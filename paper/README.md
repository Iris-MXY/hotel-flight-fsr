# 论文写作看板

本目录保存论文正文、写作状态和图表计划。根目录的 `README.md` 只负责项目导航，
方法细节放在 `docs/`，实验结果和复现脚本放在 `docs/reference/`。

## 当前快照

| 项目 | 当前状态 |
|---|---|
| 工作题目 | *A Simulation System for Future Service Rights Securitization: Architecture, Algorithms, and Machine-Learning Credit Assessment* |
| 目标类型 | CS/EI 仿真系统论文，约 9 到 10 页 |
| 当前阶段 | P0 已完成，P1 数据与特征工程待启动 |
| 稿件状态 | 英文工作稿骨架已建立，图表和参考文献待补 |
| 数据状态 | 酒店价格面板和 DB1B 航线聚合已完成 |
| 主要风险 | 四个月窗口、退出到违约的代理标签、历史脚本未完全迁入本仓库 |

## 快速入口

| 材料 | 用途 |
|---|---|
| [当前稿件](manuscript.md) | 论文正文的唯一主稿 |
| [图表计划](figures/README.md) | 计划中的主图、表格和证据来源 |
| [当前方法](../docs/PAPER_METHODS.md) | 系统、算法和实验设计 |
| [旧方法档案](../docs/OLD_METHODS.md) | 机制设计路线、Merton/KMV 失败原因和审稿口径 |
| [改稿方案](../docs/reference/REVISION_PLAN.md) | 逐节改造计划和 P0 结果 |
| [数据字典](../DATA_DICTIONARY.md) | 字段、规模、校验和与来源 |

## 贡献台账

论文当前只主张三条贡献。任何新增卖点都必须先在这里登记，并给出对应证据。

| 贡献 | 核心主张 | 现有证据 | 状态 |
|---|---|---|---|
| C1 系统与算法 | FSR 证券化仿真器支持 copula 相依抽样、现金流瀑布和并行蒙特卡洛 | 系统架构、A1 到 A4 算法说明、机票 FSR 结果 | 待正文化 |
| C2 机器学习 PD | 面板特征在完整队列上提供可用 PD；结构式基线在密集子样本上判别力弱且覆盖偏斜 | 三队列 AUC 0.8290 到 0.8956；纯价格特征 AUC 0.7474；Merton AUC 0.5644 | 已有 P0 证据 |
| C3 校准重于判别 | 判别力接近时，概率校准会显著改变分层评级 | AUC 极差 0.0355，ECE 极差 0.3050 | 已有 P0 证据 |

## 章节状态

| 章节 | 状态 | 下一步 |
|---|---|---|
| Abstract | 草稿 | 补最终仿真结果，压缩到 250 词左右 |
| 1 Introduction | 草稿 | 补常旅客证券化与超售文献 |
| 2 Related Work | 提纲 | 建立正式 BibTeX 条目 |
| 3 Problem and System | 草稿 | 补系统架构图和状态流 |
| 4 Algorithms | 草稿 | 补伪代码、复杂度和并行加速比 |
| 5 Machine-Learning PD | 草稿 | 冻结 P1 特征和验证协议 |
| 6 Experiments | 部分 | 补运行耗时、瀑布结果和下游评级 |
| 7 Discussion | 草稿 | 收敛限制表述 |
| 8 Conclusion | 提纲 | 等实验结果稳定后重写 |

## 证据登记

以下数字已经写入方法文档，可以直接用于正文草稿。引用时必须同时写出样本和口径。

| 证据 | 数值 | 来源 |
|---|---|---|
| 主队列规模 | 14,851 家酒店，正例率 7.84% | `docs/reference/REVISION_PLAN.md` |
| 三队列 LightGBM AUC | 0.8290 / 0.8675 / 0.8956 | `docs/reference/REVISION_PLAN.md` |
| 纯价格特征 AUC | 0.7474 | `docs/reference/p0_baselines.py` |
| Merton 基线 AUC | 0.5644 | `docs/reference/p0_baselines.py` |
| Merton 触顶比例 | 2,000 家中 957 家，48% | `docs/reference/p0_baselines.py` |
| 校准差距 | AUC 极差 0.0355，ECE 极差 0.3050 | `docs/reference/REVISION_PLAN.md` |
| 机票资产池 | 69 条航线，11 家航司 | `docs/PAPER_METHODS.md` |

## 写作规则

1. 每个结论必须能指回一个实验、表格或方法文档。
2. 主任务统一写 "platform exit"，不要把它直接写成 "default"。
3. 结构式模型只称为 baseline，不称为 deployed model。
4. 结构式基线所在子样本必须单独说明，不能与全队列结果直接比较。
5. 任何 PD 结果都同时报告判别力和校准指标。
6. 原型统一描述为离线仿真系统，不声称已经链上部署。
7. 待补内容使用 `[TODO: ...]` 标记，避免把占位文字当成结论。

## 下一阶段

1. 把 P0 脚本依赖的 `config.py`、`credit_model.py` 和 `robustness_checks.py`
   路径整理成可复现入口。
2. 完成 P1 的 `features.py` 和 `build_dataset.py`，冻结队列与特征清单。
3. 生成校准曲线、损失分布和并行加速比三组主图。
4. 把机票蒙特卡洛结果补入正文，并统一酒店与机票的实验口径。
5. 建立正式参考文献库，把 PDF 文件映射到 BibTeX 键。
