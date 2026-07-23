"""测试价格排序和历史收益率计算。"""

import pandas as pd
import pytest

from src.data.returns import calculate_trailing_return, prepare_price_data


def test_five_day_return_has_the_correct_direction() -> None:
    """价格从100上涨到110时，5日收益率应为正10%。"""
    prices = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-05", periods=6, freq="B"),
            "close": [100.0, 101.0, 102.0, 103.0, 104.0, 110.0],
        }
    )

    result = calculate_trailing_return(prices, periods=5)

    assert result.loc[5, "return_5d"] == pytest.approx(0.10)


def test_price_data_is_sorted_from_earliest_to_latest() -> None:
    """输入日期顺序混乱时，输出仍应按日期从早到晚排列。"""
    prices = pd.DataFrame(
        {
            "date": ["2026-01-07", "2026-01-05", "2026-01-06"],
            "close": [102.0, 100.0, 101.0],
        }
    )

    result = prepare_price_data(prices)

    assert result["date"].is_monotonic_increasing
    assert result["close"].tolist() == [100.0, 101.0, 102.0]
