"""Tests for return, compounding, volatility, and look-ahead safety.

收益率、复利、波动率与未来数据隔离测试。
"""

import numpy as np
import pandas as pd
import pytest

from src.evaluation.return_metrics import (
    calculate_annualized_volatility,
    calculate_daily_returns,
    calculate_wealth_index,
)


def make_prices(close_values: list[float]) -> pd.DataFrame:
    """Create a dated price table for concise tests.

    为简洁测试创建带日期的价格表。
    """
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-05", periods=len(close_values), freq="B"),
            "close": close_values,
        }
    )


def test_price_increase_produces_positive_simple_return() -> None:
    """A rise from 100 to 110 should produce a positive 10% return."""
    result = calculate_daily_returns(make_prices([100.0, 110.0]))

    assert result.loc[1, "simple_return"] == pytest.approx(0.10)


def test_price_decrease_produces_negative_simple_return() -> None:
    """A fall from 100 to 90 should produce a negative 10% return."""
    result = calculate_daily_returns(make_prices([100.0, 90.0]))

    assert result.loc[1, "simple_return"] == pytest.approx(-0.10)


def test_multi_period_returns_are_compounded() -> None:
    """Two 10% gains should compound to 21%, rather than add to a price series."""
    wealth = calculate_wealth_index(
        pd.Series([np.nan, 0.10, 0.10]),
        initial_wealth=1.0,
    )

    assert wealth.iloc[-1] == pytest.approx(1.21)


def test_log_return_matches_log_price_ratio() -> None:
    """Log return should equal the natural logarithm of the price ratio."""
    result = calculate_daily_returns(make_prices([100.0, 110.0]))

    assert result.loc[1, "log_return"] == pytest.approx(np.log(110.0 / 100.0))


def test_unsorted_dates_are_returned_in_chronological_order() -> None:
    """The reusable data preparation function should sort dates first."""
    prices = pd.DataFrame(
        {
            "date": ["2026-01-07", "2026-01-05", "2026-01-06"],
            "close": [102.0, 100.0, 101.0],
        }
    )

    result = calculate_daily_returns(prices)

    assert result["date"].is_monotonic_increasing
    assert result["close"].tolist() == [100.0, 101.0, 102.0]


def test_future_price_change_does_not_change_past_returns() -> None:
    """Changing future data must not alter a historical result.

    改变未来数据不能影响过去已经计算出的结果。
    """
    original = make_prices([100.0, 101.0, 102.0, 103.0])
    changed_future = make_prices([100.0, 101.0, 102.0, 500.0])

    original_result = calculate_daily_returns(original)
    changed_result = calculate_daily_returns(changed_future)

    pd.testing.assert_series_equal(
        original_result.loc[:2, "simple_return"],
        changed_result.loc[:2, "simple_return"],
    )
    pd.testing.assert_series_equal(
        original_result.loc[:2, "log_return"],
        changed_result.loc[:2, "log_return"],
    )


def test_non_unit_initial_wealth_is_respected() -> None:
    """Initial wealth of 100 with a 5% gain should finish at 105."""
    wealth = calculate_wealth_index(
        pd.Series([np.nan, 0.05]),
        initial_wealth=100.0,
    )

    assert wealth.tolist() == pytest.approx([100.0, 105.0])


@pytest.mark.parametrize("invalid_close", [0.0, -1.0])
def test_non_positive_price_raises_clear_error(invalid_close: float) -> None:
    """Zero and negative prices cannot be used inside logarithms."""
    prices = make_prices([100.0, invalid_close])

    with pytest.raises(ValueError, match="Close prices must be positive"):
        calculate_daily_returns(prices)


def test_annualized_volatility_uses_sample_standard_deviation() -> None:
    """The default ddof=1 should produce sample annualized volatility."""
    returns = pd.Series([0.01, -0.01])
    expected = returns.std(ddof=1) * np.sqrt(252)

    result = calculate_annualized_volatility(returns)

    assert result == pytest.approx(expected)
