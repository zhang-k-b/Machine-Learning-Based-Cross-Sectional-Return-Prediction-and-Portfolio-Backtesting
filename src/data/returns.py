"""价格数据排序和历史收益率计算。"""

import pandas as pd


def prepare_price_data(prices: pd.DataFrame) -> pd.DataFrame:
    """复制价格表，将日期转成时间格式，并按日期从早到晚排序。"""
    required_columns = {"date", "close"}
    missing_columns = required_columns.difference(prices.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"价格表缺少必要列：{missing_text}")

    result = prices.copy()
    result["date"] = pd.to_datetime(result["date"])
    result = result.sort_values("date").reset_index(drop=True)
    return result


def calculate_trailing_return(
    prices: pd.DataFrame,
    periods: int = 5,
) -> pd.DataFrame:
    """计算当日价格相对若干交易日前价格的历史收益率。"""
    if periods <= 0:
        raise ValueError("收益率周期必须是正整数")

    result = prepare_price_data(prices)
    return_column = f"return_{periods}d"
    result[return_column] = result["close"].pct_change(
        periods=periods,
        fill_method=None,
    )
    return result
