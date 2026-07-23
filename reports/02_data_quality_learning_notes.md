# 数据质量学习笔记

**Data Quality Learning Notes**

## 1. 为什么先检查数据

模型无法判断输入数据中的重复行、日期错误、负成交量或未来信息是不是研究者的失误。错误数据可能产生看似精确但没有经济含义的结果。

> A model can process invalid data without understanding that the data are invalid.

因此本阶段先建立“检测并报告”机制，不自动删除或修复数据。

## 2. 核心词汇 / Core vocabulary

### 2.1 data dictionary / 数据字典

**Simple English definition:** A document that defines every field, its type, meaning, unit, and permitted missingness.

中文：记录每个字段名称、含义、类型、单位、用途和缺失规则的文档。

**Professor example:**
I created a bilingual data dictionary before downloading the formal dataset so that every variable has a consistent research meaning.

### 2.2 primary key / 主键

**Simple English definition:** A field or combination of fields that uniquely identifies one observation.

中文：能够唯一确定一条观测记录的字段或字段组合。

本项目暂定主键为`security_id + date`。

**Professor example:**
The combination of security identifier and date forms the primary key of the daily panel.

### 2.3 panel data / 面板数据

**Simple English definition:** Data that follow multiple entities across multiple time periods.

中文：同时包含多个研究对象和多个时间点的数据。

本项目中，多只股票是横截面维度，交易日期是时间维度。

**Professor example:**
The dataset is a daily panel because it follows many securities through time.

### 2.4 point-in-time data / 时点一致数据

**Simple English definition:** Data recorded according to what was actually known at each historical date.

中文：按照每个历史时点当时真实可获得的信息保存的数据。

**Professor example:**
Point-in-time classifications are necessary because today’s exchange or security status may not have been valid historically.

### 2.5 missing observation / 缺失观测

**Simple English definition:** A value or row that is unavailable where an observation might otherwise be expected.

中文：在理论上可能需要数据的位置没有获得有效值。

缺失可能来自停牌、数据覆盖不足、上市初期或数据错误，不能全部用同一种方式处理。

**Professor example:**
I report missing observations by security and field rather than filling them automatically.

### 2.6 delisted security / 退市证券

**Simple English definition:** A security that has ceased trading on a covered exchange.

中文：已经停止在相关交易所挂牌交易的证券。

**Professor example:**
Delisted securities remain in the historical sample until their actual delisting dates.

### 2.7 survivorship bias / 幸存者偏差

**Simple English definition:** Bias caused by studying only entities that survived until the selection date.

中文：只研究最终仍然存在的样本，而忽略失败或消失样本造成的偏差。

**Professor example:**
I avoid defining the historical universe with today’s constituents because that would introduce survivorship bias.

### 2.8 corporate action / 公司行动

**Simple English definition:** An event such as a split, dividend, merger, or distribution that affects a security or its data.

中文：拆股、分红、并购或分配等会影响证券及数据口径的事件。

**Professor example:**
Corporate actions must be handled consistently to prevent artificial jumps in price-based factors.

### 2.9 data validation / 数据验证

**Simple English definition:** A systematic process for checking whether data satisfy defined structural and numerical rules.

中文：根据预先定义的结构和数值规则系统检查数据的过程。

**Professor example:**
The validation module detects duplicate keys and invalid values without silently changing the source data.

### 2.10 audit trail / 审计轨迹

**Simple English definition:** A traceable record of what was changed, when, why, and by which rule.

中文：记录何时、为什么、按照什么规则进行数据处理的可追踪记录。

**Professor example:**
Every cleaning decision should leave an audit trail so that the processed dataset can be reproduced.

## 3. 检测与修复的区别

### Detection / 检测

回答：

- 哪里有问题？
- 问题有多少？
- 涉及哪些证券和日期？
- 违反了哪条规则？

### Correction / 修复

回答：

- 应该删除、保留、替换还是重新下载？
- 修复是否改变研究样本？
- 修复需要什么经济或数据源依据？

本阶段只执行检测，因为自动修复可能掩盖真正的数据问题。

> Detection is mechanical; correction often requires research judgment.

## 4. 为什么不自动删除异常

负成交量通常像数据错误，但极端收益可能来自真实拆股、并购或退市。如果验证程序直接删除所有异常：

- 可能删掉真实市场事件；
- 可能改变股票池；
- 可能降低退市和危机样本比例；
- 可能让回测结果人为改善；
- 可能失去可复现的处理记录。

正确流程：

```text
检测 → 报告 → 查看数据源和经济原因 → 记录决定 → 单独清洗
```

## 5. 基础验证规则

### 必要字段

缺少日期、证券编号、收盘价、成交量或总收益时，验证无法继续完成核心检查。

### 主键重复

同一`security_id + date`出现多次，可能导致重复计算收益或重复持仓。

### 日期

无法解析的日期不能参与排序、滚动窗口和时间切分。

### 股票内部排序

整个表格看似有序，不代表每只股票内部有序。滚动因子必须在证券内部按时间计算。

### 价格

有效非缺失价格必须大于0。缺失价格与非正价格是两种不同问题。

### 成交量

成交量可以为0，但不能小于0。0可能代表没有成交，缺失则代表不知道。

### 收益率

普通简单收益率不能低于-100%。异常值应先核对单位、公司行动和退市处理。

### 有效交易日

本阶段暂定：日期有效、收盘价为正且成交量非负的唯一日期，计为一个基础有效交易日。正式研究可能根据数据源字段增加更严格定义。

## 6. 与未来数据泄漏的关系

数据质量处理本身也可能泄漏未来信息。例如：

- 使用完整样本均值填补早期缺失值；
- 用未来价格回填停牌期间价格；
- 用今天的证券类型修正全部历史；
- 根据测试期缺失率决定训练期筛选规则；
- 先看未来退市结果，再删除早期观测。

> Data cleaning must also obey the information set available at each historical date.

## 7. 研究者应保留的记录

每次处理正式数据，应记录：

- 原始行数；
- 重复主键数量；
- 无效日期数量；
- 各字段缺失数量；
- 非正价格数量；
- 负成交量数量；
- 异常收益数量；
- 各证券有效交易日数量；
- 每项清洗决定；
- 清洗前后行数。

## 8. Communicating with a professor

1. **I define the schema before downloading the formal data.**
2. **The validation layer reports anomalies but does not silently delete them.**
3. **The daily panel is uniquely identified by security identifier and date.**
4. **Each security must be checked in its own chronological order.**
5. **Missing values are documented because different missingness mechanisms require different treatment.**
6. **Every later cleaning decision will leave an audit trail.**

## 9. 本阶段边界

本阶段没有：

- 下载CRSP数据；
- 建立真实股票池；
- 自动修复异常；
- 计算正式因子；
- 构建未来收益标签；
- 训练模型；
- 运行投资组合回测。

The output of this stage is a research specification and a validation framework, not a cleaned market dataset.
