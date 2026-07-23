# 研究设计、数据字典与数据质量

**Research Design, Data Dictionary, and Data Quality**

## 1. 研究目标 / Research objective

本项目研究少量、容易解释的价格与成交量因子能否预测美国普通股未来5个交易日的横截面相对收益。研究将严格区分因子形成时间、组合形成时间和未来收益实现时间。

This project studies whether a small set of interpretable price- and volume-based factors can predict five-trading-day cross-sectional relative returns among US common stocks.

项目目标是建立方法正确、透明和可复现的研究流程，而不是证明能够实盘盈利。

## 2. 暂定研究设计 / Proposed research design

| 项目 | 暂定选择 |
|---|---|
| 市场 | 美国普通股 / US common stocks |
| 正式数据源 | CRSP via WRDS |
| 研究时间 | 2010-01-01至2024-12-31 |
| 预测目标 | 未来5个交易日相对收益 |
| 股票池更新 | 每月一次 |
| 流动性窗口 | 截至上月末的过去60个交易日 |
| 股票数量 | 合格股票中成交额最高的200只 |
| 训练集 | 2010—2018 |
| 验证集 | 2019—2021 |
| 测试集 | 2022—2024 |
| 集合边界 | 至少5个交易日的隔离区 |

## 3. 为什么选择美国股票 / Why US stocks

第一个研究版本选择美国普通股，主要因为：

1. CRSP是学术金融研究中常用的证券数据库；
2. 它提供永久证券编号、历史交易状态、公司行动和退市信息；
3. 美国数据的研究惯例和字段定义相对标准化；
4. 它适合系统学习幸存者偏差、退市收益和point-in-time股票池；
5. 可以先聚焦通用研究方法，而不同时处理A股ST、涨跌停和长期停牌等额外制度细节。

> I chose US common stocks because CRSP provides permanent identifiers, historical security status, corporate actions, and delisting information that support a point-in-time research design.

选择美国市场不表示它更容易获得高收益，也不表示研究结论可以自动推广到中国市场。

## 4. WRDS、CRSP和CSMAR / Data platforms and databases

### WRDS

**Wharton Research Data Services**是学术研究数据访问平台。它类似一个数据库入口，研究者可以通过它访问CRSP、Compustat等数据资源。

### CRSP

**Center for Research in Security Prices**通常指其美国证券研究数据库。它提供价格、收益率、成交量、证券标识、公司行动、交易状态和退市信息。

自然英文表达：

> The formal dataset will be obtained from CRSP through WRDS.

### CSMAR

**China Stock Market & Accounting Research Database**主要覆盖中国股票市场、公司财务、治理和经济研究数据。如果将来把研究迁移到中国A股，CSMAR是更合适的正式数据源之一。

本阶段只确定数据计划，不登录、查询或下载上述数据库。

## 5. 为什么不能使用今天的指数成分股回看历史

如果先取得今天仍在指数中的公司名单，再将它们用于2010年的研究，就会系统性排除：

- 已经退市的公司；
- 破产或经营失败的公司；
- 被指数移除的公司；
- 被收购或合并后消失的证券。

这会产生幸存者偏差，使历史股票池看起来比当时真实可投资的股票池更成功。

> Using today’s constituents to define a historical universe would exclude firms that disappeared and introduce survivorship bias.

## 6. 动态股票池 / Dynamic investment universe

股票池每月重新形成一次，并从下个月开始生效。

在每个月最后一个交易日：

1. 使用当时有效的证券类型和交易所信息筛选美国普通股；
2. 使用截至当日已经获得的历史数据；
3. 计算过去60个交易日的日成交额；
4. 用过去60日成交额的中位数衡量流动性；
5. 排除历史窗口不足或核心数据不足的证券；
6. 在合格股票中选择流动性最高的200只；
7. 将名单用于下一个月，而不是追溯应用于本月。

日成交额的研究定义暂定为：

\[
\text{Dollar Volume}_{i,t}
=
\text{Raw Close}_{i,t}
\times
\text{Raw Volume}_{i,t}
\]

使用中位数而不是单日成交额，可以降低异常大额交易对流动性排序的影响。

动态股票池可以让新上市、退市和流动性变化逐步进入研究过程。它能降低幸存者偏差，但不能自动消除全部样本选择偏差。

## 7. 未来5日相对收益标签

个股未来5个交易日总收益暂定为：

\[
R^{(5)}_{i,t}
=
\prod_{k=1}^{5}(1+R_{i,t+k})-1
\]

横截面相对收益可定义为：

\[
Y_{i,t}
=
R^{(5)}_{i,t}
-
\frac{1}{N_t}\sum_{j=1}^{N_t}R^{(5)}_{j,t}
\]

其中：

- \(Y_{i,t}\)是股票\(i\)在日期\(t\)对应的预测标签；
- \(N_t\)是当期股票池中的股票数量；
- 未来收益只在训练时作为结果变量使用。

### 为什么只能作为标签

日期\(t\)做决策时，\(t+1\)至\(t+5\)的价格尚不可知。如果未来收益进入因子、标准化、股票池筛选或缺失值处理，就会产生未来数据泄漏。

> Future returns define the prediction target, but they must never enter the feature set or universe-selection process.

## 8. 为什么时间序列不能随机切分

随机切分会把较晚年份的样本放入训练集，同时把较早年份的样本放入测试集。模型因此可能间接学习未来市场制度、波动环境和数据分布。

本项目采用：

```text
2010—2018：训练集
至少5个交易日隔离区
2019—2021：验证集
至少5个交易日隔离区
2022—2024：测试集
```

隔离区用于防止5日未来收益标签跨越不同数据集合的边界。边界的正式实现将在标签模块中根据交易日历精确完成。

> A chronological split preserves the direction of time, while a boundary gap prevents forward-return labels from overlapping adjacent datasets.

## 9. 数据质量原则 / Data-quality principles

1. 原始数据不手工覆盖；
2. 验证程序只报告问题，不自动修正；
3. 每一步清洗记录输入和输出行数；
4. 缺失、重复、无效日期和极端值分别统计；
5. 所有筛选规则使用当时已经获得的信息；
6. 数据源字段先映射到项目内部数据字典；
7. 公司行动调整不能重复进行；
8. 退市股票保留至实际退市时点；
9. 所有质量报告都应可以重新生成；
10. 任何人工决定都写入audit trail。

## 10. 当前限制 / Current limitations

本研究设计仍有以下限制：

- 尚未确认个人是否拥有WRDS/CRSP访问权限；
- 尚未检查CRSP当前下载格式中退市收益是否已计入总收益；
- 200只股票和60日窗口仍是研究选择，需要稳健性比较；
- 流动性筛选可能减少对小盘股的代表性；
- 5日标签可能存在相邻样本重叠问题；
- 交易成本参数尚未用真实市场数据校准；
- 当前数据验证仅针对表格结构和基础数值逻辑；
- 尚未处理公司更名、并购和复杂证券映射；
- 本阶段没有真实数据，因此没有实际缺失率或异常率结论；
- 美国市场结论不能直接推广到中国市场。

## 11. Communicating with a professor

I propose to study US common stocks using CRSP data accessed through WRDS. The sample will cover 2010 to 2024 and will be split chronologically into training, validation, and test periods, with a five-trading-day gap at each boundary. Rather than using today’s index constituents, I will reconstruct the universe monthly using only information available at the previous month-end. Among eligible securities, the 200 stocks with the highest trailing 60-day dollar volume will be selected. Future five-day relative returns will be used only as labels. At this stage, I am documenting the data schema and validation rules before downloading formal market data.

## 12. 参考资料 / References

- [UNNC Business, Finance and Economic Resources](https://www.nottingham.edu.cn/en/library/finding-resources/subject-resources/business-finance-and-economic-resources.aspx)
- [CRSP US Stock and Indexes Data Guide](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-guide-flat-file-format-2-0/)
