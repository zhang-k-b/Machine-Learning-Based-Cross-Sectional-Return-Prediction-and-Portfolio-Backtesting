# 双语数据字典

**Bilingual Data Dictionary**

## 1. 数据字典的作用

数据字典记录每个字段的定义、类型、缺失规则、用途和时间含义。它可以防止不同模块对同一字段产生不一致理解。

> A data dictionary defines the meaning, type, permitted missingness, research use, and temporal interpretation of every field.

本文件使用项目内部统一字段名。正式下载CRSP数据后，需要另外记录原始CRSP字段到内部字段的映射，不能只凭字段名称猜测含义。

## 2. 主键 / Primary key

暂定主键：

```text
security_id + date
```

同一证券在同一交易日原则上只能出现一行。`ticker`不能作为永久主键，因为股票代码可能因更名、并购或公司行动而改变。

## 3. 字段定义

### 3.1 `date`

| 属性 | 定义 |
|---|---|
| 中文名称 | 交易日期 |
| English definition | The calendar date associated with the security observation. |
| 数据类型 | `datetime64[ns]` |
| 允许缺失 | 否 |
| 用途 | 主键、时间排序、时间切分、质量检查 |
| 泄漏风险 | 中等：如果日期错位，未来价格可能被错误对齐到过去 |

要求使用明确的日期格式，并在处理后转换为统一时区或无时区日频日期。

### 3.2 `security_id`

| 属性 | 定义 |
|---|---|
| 中文名称 | 永久证券编号 |
| English definition | A stable identifier assigned to a security across ticker or name changes. |
| 数据类型 | 字符串或整数，但全项目必须统一 |
| 允许缺失 | 否 |
| 用途 | 主键、分组计算、历史证券追踪 |
| 泄漏风险 | 低；但不能用当前Ticker代替历史永久编号 |

CRSP研究中通常使用类似PERMNO的永久证券标识。

### 3.3 `ticker`

| 属性 | 定义 |
|---|---|
| 中文名称 | 股票代码 |
| English definition | The trading symbol valid for the security at the observation date. |
| 数据类型 | 字符串 |
| 允许缺失 | 可以短暂缺失，但必须报告 |
| 用途 | 展示、人工检查、外部匹配 |
| 泄漏风险 | 中等：使用当前Ticker回填全部历史可能造成错误映射 |

`ticker`用于阅读，不作为唯一主键。

### 3.4 `exchange_code`

| 属性 | 定义 |
|---|---|
| 中文名称 | 交易所代码 |
| English definition | The exchange classification that was valid on the observation date. |
| 数据类型 | 分类字符串或整数代码 |
| 允许缺失 | 原则上不允许；缺失必须报告 |
| 用途 | 股票池筛选、描述统计、质量检查 |
| 泄漏风险 | 高：必须使用历史时点的交易所归属，不能使用今天的归属 |

### 3.5 `security_type`

| 属性 | 定义 |
|---|---|
| 中文名称 | 证券类型 |
| English definition | The point-in-time classification of the security, such as common stock or ETF. |
| 数据类型 | 分类字符串或整数代码 |
| 允许缺失 | 原则上不允许 |
| 用途 | 筛选美国普通股，排除ETF和其他证券 |
| 泄漏风险 | 高：必须使用当时有效的分类 |

### 3.6 `open_raw`

| 属性 | 定义 |
|---|---|
| 中文名称 | 未复权开盘价 |
| English definition | The first recorded trading price of the regular session before project-level adjustment. |
| 数据类型 | 浮点数 |
| 允许缺失 | 是，例如无有效开盘交易 |
| 用途 | 可选执行价格、价格逻辑检查 |
| 泄漏风险 | 中等：必须与实际交易时间和信号形成时间正确对齐 |

### 3.7 `close_raw`

| 属性 | 定义 |
|---|---|
| 中文名称 | 未复权收盘价 |
| English definition | The closing price before project-level corporate-action adjustment. |
| 数据类型 | 浮点数 |
| 允许缺失 | 可以因停牌等原因缺失，但属于核心质量问题 |
| 用途 | 价格筛选、成交额、质量检查 |
| 泄漏风险 | 中等：不能用未来价格回填当前缺失价格 |

有效非缺失价格必须大于0。

### 3.8 `volume_raw`

| 属性 | 定义 |
|---|---|
| 中文名称 | 原始成交量 |
| English definition | The reported number of shares traded during the observation date before project-level adjustment. |
| 数据类型 | 非负整数或浮点数 |
| 允许缺失 | 是，但必须统计 |
| 用途 | 流动性因子、股票池筛选、质量检查 |
| 泄漏风险 | 中等：60日窗口必须在股票池形成日之前结束 |

成交量不能小于0；零成交量与缺失成交量不能自动视为相同含义。

### 3.9 `total_return`

| 属性 | 定义 |
|---|---|
| 中文名称 | 总收益率 |
| English definition | The holding-period return including eligible distributions and corporate-action effects. |
| 数据类型 | 浮点数，以小数表示 |
| 允许缺失 | 是，但必须记录原因 |
| 用途 | 因子、未来标签、投资组合收益、质量检查 |
| 泄漏风险 | 高：未来区间总收益只能作为标签，不能进入当期特征 |

有效收益率原则上不能低于-100%。必须确认数据源是否已经包含退市收益，避免重复处理。

### 3.10 `price_return`

| 属性 | 定义 |
|---|---|
| 中文名称 | 价格收益率 |
| English definition | The holding-period return from price appreciation, excluding ordinary cash dividends. |
| 数据类型 | 浮点数 |
| 允许缺失 | 是 |
| 用途 | 与总收益对照、公司行动和股息检查 |
| 泄漏风险 | 高：任何未来价格收益都只能用于标签或事后评价 |

### 3.11 `shares_outstanding`

| 属性 | 定义 |
|---|---|
| 中文名称 | 发行在外股数 |
| English definition | The number of shares outstanding reported for the security at the relevant date. |
| 数据类型 | 非负浮点数或整数 |
| 允许缺失 | 是，缺失时市值也应标记 |
| 用途 | 市值计算、描述统计、可选股票池筛选 |
| 泄漏风险 | 高：财务或股数信息必须按真实发布日期和生效日期对齐 |

### 3.12 `market_cap`

| 属性 | 定义 |
|---|---|
| 中文名称 | 市值 |
| English definition | The market value of equity derived from price and shares outstanding. |
| 数据类型 | 非负浮点数 |
| 允许缺失 | 是 |
| 用途 | 描述统计、可选规模筛选、规模因子 |
| 泄漏风险 | 高：价格和股数必须来自同一可得时点 |

暂定计算：

\[
\text{Market Cap}_{i,t}
=
|\text{Close Raw}_{i,t}|
\times
\text{Shares Outstanding}_{i,t}
\]

需要根据数据源确认股数单位。

### 3.13 `price_adjustment_factor`

| 属性 | 定义 |
|---|---|
| 中文名称 | 价格调整因子 |
| English definition | A factor used to place prices on a consistent basis across splits or distributions. |
| 数据类型 | 正浮点数或数据源规定的因子类型 |
| 允许缺失 | 取决于数据源；缺失必须检查 |
| 用途 | 公司行动调整、价格一致性检查 |
| 泄漏风险 | 中等：错误方向或重复复权会扭曲历史收益 |

不能同时使用已经复权的价格和调整因子再次复权。

### 3.14 `delisting_return`

| 属性 | 定义 |
|---|---|
| 中文名称 | 退市收益率 |
| English definition | The return from the final trading value to the value received after delisting. |
| 数据类型 | 浮点数 |
| 允许缺失 | 非退市股票为空；退市股票缺失必须报告 |
| 用途 | 退市处理、总收益检查、幸存者偏差控制 |
| 泄漏风险 | 高：只能在退市信息实际生效后用于收益计算 |

需要确认正式CRSP格式是否已将退市收益计入`total_return`。

### 3.15 `delisting_code`

| 属性 | 定义 |
|---|---|
| 中文名称 | 退市原因代码 |
| English definition | A code describing the reason or category of a security delisting. |
| 数据类型 | 分类字符串或整数 |
| 允许缺失 | 非退市股票允许为空 |
| 用途 | 退市质量检查、缺失退市收益分析 |
| 泄漏风险 | 高：不能在退市发生前将未来退市状态作为因子 |

### 3.16 `trading_status`

| 属性 | 定义 |
|---|---|
| 中文名称 | 交易状态 |
| English definition | The point-in-time status indicating whether the security is active, halted, suspended, or delisted. |
| 数据类型 | 分类字符串 |
| 允许缺失 | 原则上不允许 |
| 用途 | 可交易性判断、停牌和退市检查 |
| 泄漏风险 | 高：必须使用当时状态，不能提前知道未来停牌或退市 |

## 4. 数据类型与单位规则

- 所有收益率以小数表示，例如5%写作`0.05`；
- 所有价格使用美元，除非数据源另有明确货币字段；
- 成交量单位必须记录为股数还是手数；
- 股数单位必须确认是否已经按千股存储；
- 日期必须采用统一格式；
- 分类代码必须保留原始值与解释映射；
- 派生字段需要记录公式和输入字段。

## 5. 缺失值原则

“允许缺失”不代表可以忽略。每个缺失值至少需要回答：

1. 是正常结构性缺失还是数据错误？
2. 是否与停牌、上市初期或退市有关？
3. 是否会影响因子、标签或股票池？
4. 是否需要排除当前股票—日期观测？
5. 决策是否写入audit trail？

本阶段的数据验证只报告缺失数量，不自动填补。

## 6. 版本与审计

正式数据到达后，应在本文件补充：

- 数据库名称和版本；
- 下载日期；
- 查询条件；
- 原始字段名；
- 内部字段映射；
- 单位换算；
- 公司行动处理；
- 人工判断记录。

> The data dictionary must evolve with the dataset, but every change should remain traceable.
