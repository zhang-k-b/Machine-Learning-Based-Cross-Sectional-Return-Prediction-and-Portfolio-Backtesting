# 收益率、复利与风险基础

**Return, Compounding, and Risk Fundamentals**

## 1. 本阶段目标 / Learning objectives

这一阶段不预测股票，也不判断策略是否盈利。目标是先验证金融研究最基础的计算：价格如何转化为收益率、收益率如何通过复利形成财富，以及如何用波动率描述收益的不稳定程度。

This lesson validates the financial calculations that later models and backtests will depend on. Synthetic data are used so that every result can be checked by hand.

## 2. 四个核心公式 / Four core formulas

### 2.1 简单收益率 / Simple return

\[
R_t = \frac{P_t}{P_{t-1}} - 1
\]

- \(P_t\)：当期价格 / current price
- \(P_{t-1}\)：前一期价格 / previous-period price
- \(R_t\)：从 \(t-1\) 到 \(t\) 的简单收益率 / one-period simple return

简单收益率表示投入1元后在一个持有期内获得的百分比变化。例如，价格从100上涨到110，简单收益率为10%。

A simple return measures the percentage change in an investment over one holding period.

### 2.2 对数收益率 / Log return

\[
r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)
\]

- \(\ln\)：自然对数 / natural logarithm
- \(r_t\)：对数收益率 / continuously compounded log return

对数收益率在时间维度上可以直接相加：

\[
\sum_{t=1}^{T} r_t = \ln\left(\frac{P_T}{P_0}\right)
\]

Log returns are additive over time because the logarithm converts multiplication of price ratios into addition.

### 2.3 累计财富 / Cumulative wealth

\[
W_t = W_0 \prod_{i=1}^{t}(1+R_i)
\]

- \(W_0\)：初始财富 / initial wealth
- \(W_t\)：第 \(t\) 期累计财富 / cumulative wealth at time \(t\)
- \(\prod\)：连续相乘 / product across periods

多期简单收益率必须复利连接，不能直接相加。例如：

```text
初始财富 = 1.00
第一期上涨10%：1.00 × 1.10 = 1.10
第二期下跌10%：1.10 × 0.90 = 0.99
最终累计收益 = -1%
```

An increase of 10% followed by a decrease of 10% does not return the investment to its starting value.

### 2.4 年化波动率 / Annualized volatility

\[
\sigma_{\text{annual}} = \sigma_{\text{daily}}\sqrt{252}
\]

- \(\sigma_{\text{daily}}\)：日收益率标准差 / standard deviation of daily returns
- \(252\)：一年中常用的交易日数量假设 / assumed trading days per year
- \(\sigma_{\text{annual}}\)：年化波动率 / annualized volatility

时间平方根法则假设日收益率的方差可以随时间近似线性累积，通常还隐含收益率分布较稳定、序列相关性较弱等条件。现实市场可能存在波动聚集和结构变化，因此它是常用估计，不是永远成立的自然定律。

The square-root-of-time rule is a convention based on simplifying assumptions. It can be inaccurate when returns are serially correlated or volatility changes over time.

## 3. 简单收益率与对数收益率 / Simple versus log returns

| 比较 | 简单收益率 / Simple return | 对数收益率 / Log return |
|---|---|---|
| 公式 | \(P_t/P_{t-1}-1\) | \(\ln(P_t/P_{t-1})\) |
| 时间聚合 | 通过复利相乘 | 可以直接相加 |
| 直观解释 | 实际百分比盈亏 | 连续复利收益 |
| 常见用途 | 投资组合表现和财富计算 | 时间序列建模与统计分析 |
| 限制 | 不能跨期直接相加 | 不适合直接按资产权重求组合收益 |

当收益率很小时，两者数值接近，但不完全相同。实际投资组合财富通常使用简单收益率复利计算；对数收益率在时间序列分析中很方便。

Simple returns are intuitive for portfolio performance, whereas log returns are convenient for time-series aggregation.

## 4. 样本标准差与总体标准差 / Sample and population standard deviation

代码默认使用`ddof=1`，即样本标准差。因为观察到的历史收益通常被视为来自更广泛但未知的收益生成过程，样本标准差使用 \(n-1\) 作为分母以估计未知总体波动率。

- `ddof=1`：样本标准差 / sample standard deviation
- `ddof=0`：总体标准差 / population standard deviation

The project uses sample standard deviation by default because historical observations are treated as a sample from an unknown return-generating process.

## 5. 代码的输入与输出 / Code inputs and outputs

### `calculate_daily_returns`

输入：

- 包含`date`和`close`列的`pandas.DataFrame`。

输出：

- 按日期从早到晚排列的数据；
- `simple_return`；
- `log_return`。

### `calculate_wealth_index`

输入：

- 简单收益率序列；
- 初始财富。

输出：

- 使用 \((1+R_t)\) 连续相乘得到的`wealth_index`。

### `calculate_annualized_volatility`

输入：

- 日简单收益率；
- 年交易日数量；
- 标准差自由度`ddof`。

输出：

- 年化波动率浮点数。

## 6. 为什么没有未来数据泄漏 / Why there is no look-ahead bias

日收益率只使用：

```text
当前价格 P_t
前一期价格 P_(t-1)
```

代码通过`shift(1)`取得过去价格，没有使用`shift(-1)`或未来价格。自动测试还会修改最后一个未来价格，并确认此前日期的收益率完全不变。

Each historical return depends only on the current and previous observations. Changing a future price cannot alter an already calculated historical return.

这一点不代表整个未来项目已经自动避免泄漏。以后计算预测标签时会使用未来收益，但标签必须与输入因子严格分开。

## 7. 金融含义 / Financial interpretation

- **简单收益率**：投资者一个持有期内实际百分比变化的直观表达。
- **对数收益率**：价格比例的对数表示，适合跨时间相加和统计建模。
- **累计财富**：1元初始投资经过连续复利后变成多少。
- **波动率**：收益率围绕均值变化的程度，是风险的一种代理变量，但不能概括所有风险。

Volatility measures dispersion, not the probability of every possible loss. It does not directly capture liquidity risk, model risk, tail risk, or permanent capital loss.

## 8. 为什么高收益不能单独证明模型优秀

高收益可能来自：

- 承担了更高风险；
- 少数极端行情；
- 数据泄漏；
- 幸存者偏差；
- 忽略交易成本；
- 反复调整参数后选择最好结果；
- 偶然性。

因此还需要评价波动率、最大回撤、换手率、样本外表现、稳健性和基准比较。

A high return alone is not evidence of a robust model. Risk, costs, bias, and out-of-sample stability must also be evaluated.

## 9. 为什么先验证收益率，再使用机器学习

机器学习模型最终预测或排序的是未来收益。如果收益标签、复利或波动率计算有错误，复杂模型只会更快地放大错误。先使用可手算的模拟数据验证基础函数，可以建立可信、可测试、可复现的研究流程。

I validate the return mechanics before introducing machine learning because model quality cannot compensate for an incorrectly defined target.

## 10. 常见错误 / Common mistakes

1. 把多期简单收益率直接相加；
2. 使用今天的价格计算昨天本应未知的指标；
3. 用`shift(-1)`构造标签后误把标签放进特征；
4. 将缺失收益率全部替换成0；
5. 在拆股数据中重复进行价格复权；
6. 把波动率等同于全部风险；
7. 看到高累计收益就忽略回撤和交易成本；
8. 混淆10%的收益率与10个百分点。

## 11. 专业词汇 / Professional vocabulary

| English | 中文 | Simple English definition | Example for a professor |
|---|---|---|---|
| simple return | 简单收益率 | The percentage change in value over one period. | I use simple returns to construct the portfolio wealth index. |
| log return | 对数收益率 | The natural logarithm of the price ratio. | Log returns are useful because they are additive over time. |
| compounding | 复利 | The process of earning returns on previous gains or losses. | I compound simple returns rather than adding them across periods. |
| cumulative wealth | 累计财富 | The value of an initial investment after repeated returns. | The cumulative wealth curve shows how one unit of capital evolves. |
| volatility | 波动率 | A measure of how widely returns vary. | Volatility is one risk measure, but it does not capture every form of risk. |
| annualized volatility | 年化波动率 | Daily return volatility expressed on an annual scale. | I annualize daily volatility using the square-root-of-time convention. |
| risk-adjusted return | 风险调整后收益 | Return evaluated relative to the risk taken. | I will compare models using risk-adjusted return, not raw return alone. |
| look-ahead bias | 前视偏差、未来数据泄漏 | Bias caused by using information unavailable at the decision time. | I added a test to ensure that future prices cannot change past features. |
| out-of-sample test | 样本外测试 | Evaluation on data not used to fit or select the model. | The final comparison will rely on a strictly time-ordered out-of-sample test. |
| reproducibility | 可复现性 | The ability to obtain the same result from the same data and method. | Automated tests and fixed definitions improve the reproducibility of my study. |

## 12. Communicating with a Professor

1. **I started by validating the return calculations before introducing any machine learning model.**
2. **At this stage, I use synthetic data because the purpose is to verify the method rather than claim predictive performance.**
3. **Multi-period simple returns are linked multiplicatively through compounding.**
4. **Log returns are additive across time because log price ratios can be summed.**
5. **Every metric in this lesson uses only information available at or before time \(t\).**
6. **The current results do not imply that the strategy would be profitable in live trading.**
7. **The next step is to examine real-data quality, delistings, missing observations, and survivorship bias.**

### 80—120 word project update

At the current stage, I have implemented and tested a small return-and-risk module using synthetic price data. The module calculates simple returns, log returns, cumulative wealth, and annualized volatility. I deliberately began with transparent calculations that can be verified by hand before introducing real market data or machine learning. The code sorts observations chronologically and uses only current and past prices. I also added a test showing that changing a future price cannot alter previously calculated returns. This helps guard against look-ahead bias. The next stage will focus on data-source selection, missing observations, delistings, corporate actions, and survivorship bias before any predictive model is trained.

## 13. 本阶段边界 / Scope boundary

本阶段只证明基础计算按照定义工作。它没有证明：

- 模拟价格代表真实市场；
- 某个因子具有预测能力；
- 某个策略能够盈利；
- 年化波动率假设在所有时期都成立；
- 整个未来回测已经不存在任何偏差。

The result is a verified calculation module, not a trading strategy.
