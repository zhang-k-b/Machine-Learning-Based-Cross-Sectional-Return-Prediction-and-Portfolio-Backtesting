"""Return, compounding, and volatility calculations.

收益率、复利与波动率计算。
"""

import numpy as np
import pandas as pd

from src.config import TRADING_DAYS_PER_YEAR
from src.data.returns import prepare_price_data


def calculate_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate one-period simple and log returns from historical prices.

    使用历史价格计算单期简单收益率和对数收益率。
    """
    result = prepare_price_data(prices)
    if result["close"].isna().any():
        raise ValueError("收盘价不能包含缺失值 / Close prices cannot contain missing values")
    if (result["close"] <= 0).any():
        raise ValueError("收盘价必须大于0 / Close prices must be positive")

    previous_close = result["close"].shift(1)
    result["simple_return"] = result["close"] / previous_close - 1
    result["log_return"] = np.log(result["close"] / previous_close)
    return result


def calculate_wealth_index(
    simple_returns: pd.Series,
    initial_wealth: float = 1.0,
) -> pd.Series:
    """Compound simple returns into a cumulative wealth index.

    将简单收益率按复利方式连接成累计财富指数。
    """
    if initial_wealth <= 0:
        raise ValueError("初始财富必须大于0 / Initial wealth must be positive")

    returns = pd.Series(simple_returns, copy=True, dtype=float)
    if returns.empty:
        raise ValueError("收益率序列不能为空 / Return series cannot be empty")
    if (~np.isfinite(returns.dropna())).any():
        raise ValueError("收益率必须是有限数值 / Returns must be finite")
    if (returns.dropna() < -1).any():
        raise ValueError("简单收益率不能小于-100% / Simple returns cannot be below -100%")

    # The first missing return represents the starting observation, not a gain or loss.
    # 第一行缺失收益率代表起始时点，不代表盈利或亏损。
    if pd.isna(returns.iloc[0]):
        returns.iloc[0] = 0.0
    if returns.iloc[1:].isna().any():
        raise ValueError(
            "除第一行外不能有缺失收益率 / Missing returns are only allowed in the first row"
        )

    wealth_index = initial_wealth * (1 + returns).cumprod()
    wealth_index.name = "wealth_index"
    return wealth_index


def calculate_annualized_volatility(
    simple_returns: pd.Series,
    trading_days: int = TRADING_DAYS_PER_YEAR,
    ddof: int = 1,
) -> float:
    """Annualize daily return volatility using the square-root-of-time rule.

    使用时间平方根法则将日收益率波动率年化。
    """
    if trading_days <= 0:
        raise ValueError("年交易日数量必须为正数 / Trading days must be positive")
    if ddof < 0:
        raise ValueError("自由度不能为负数 / Degrees of freedom cannot be negative")

    returns = pd.Series(simple_returns, copy=True, dtype=float).dropna()
    if (~np.isfinite(returns)).any():
        raise ValueError("收益率必须是有限数值 / Returns must be finite")
    if len(returns) <= ddof:
        raise ValueError(
            "有效收益率数量不足 / Not enough valid returns for the selected ddof"
        )

    daily_volatility = returns.std(ddof=ddof)
    return float(daily_volatility * np.sqrt(trading_days))
