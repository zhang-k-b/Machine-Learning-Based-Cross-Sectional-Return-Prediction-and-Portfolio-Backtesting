"""Tests for non-destructive panel-data validation.

非破坏性面板数据验证测试。
"""

import pandas as pd
import pytest

from src.data.validation import (
    check_required_columns,
    find_duplicate_primary_keys,
    find_invalid_dates,
    find_negative_volumes,
    find_non_positive_prices,
    find_returns_below_minus_one,
    find_unsorted_securities,
    validate_panel_data,
)


def make_clean_panel() -> pd.DataFrame:
    """Create a minimal clean two-security panel.

    创建最小的两证券干净面板。
    """
    return pd.DataFrame(
        {
            "security_id": ["A", "A", "B", "B"],
            "date": [
                "2024-01-02",
                "2024-01-03",
                "2024-01-02",
                "2024-01-03",
            ],
            "open_raw": [99.5, 100.5, 49.5, 50.5],
            "close_raw": [100.0, 101.0, 50.0, 51.0],
            "volume_raw": [1000, 1100, 2000, 2100],
            "total_return": [0.00, 0.01, 0.00, 0.02],
            "price_return": [0.00, 0.01, 0.00, 0.02],
        }
    )


def test_clean_data_passes_all_checks() -> None:
    """A clean panel should receive an overall valid result."""
    report = validate_panel_data(make_clean_panel())

    assert report["is_valid"] is True
    assert report["valid_trading_day_counts"] == {"A": 2, "B": 2}


def test_missing_required_column_raises_error() -> None:
    """Validation cannot proceed without a required field."""
    data = make_clean_panel().drop(columns="volume_raw")

    with pytest.raises(ValueError, match="Missing required columns: volume_raw"):
        check_required_columns(data)


def test_duplicate_primary_key_is_detected() -> None:
    """Both rows involved in a duplicate key should be reported."""
    data = pd.concat(
        [make_clean_panel(), make_clean_panel().iloc[[0]]],
        ignore_index=True,
    )

    duplicates = find_duplicate_primary_keys(data)

    assert len(duplicates) == 2
    assert duplicates["security_id"].tolist() == ["A", "A"]


def test_non_positive_price_is_detected() -> None:
    """Zero and negative prices should be reported."""
    data = make_clean_panel()
    data.loc[0, "close_raw"] = 0.0

    invalid_prices = find_non_positive_prices(data)

    assert invalid_prices.index.tolist() == [0]


def test_negative_volume_is_detected() -> None:
    """Negative volume is invalid, while zero volume is not negative."""
    data = make_clean_panel()
    data.loc[1, "volume_raw"] = -1
    data.loc[2, "volume_raw"] = 0

    invalid_volumes = find_negative_volumes(data)

    assert invalid_volumes.index.tolist() == [1]


def test_invalid_date_is_detected() -> None:
    """An unparseable date should be reported."""
    data = make_clean_panel()
    data.loc[2, "date"] = "not-a-date"

    invalid_dates = find_invalid_dates(data)

    assert invalid_dates.index.tolist() == [2]


def test_each_security_is_checked_in_its_own_order() -> None:
    """Only the security with reversed internal dates should be reported."""
    data = make_clean_panel()
    data.loc[0, "date"] = "2024-01-03"
    data.loc[1, "date"] = "2024-01-02"

    unsorted = find_unsorted_securities(data)

    assert unsorted == ["A"]


def test_return_below_minus_one_is_detected() -> None:
    """A simple return below negative 100% should be reported."""
    data = make_clean_panel()
    data.loc[3, "total_return"] = -1.01

    invalid_returns = find_returns_below_minus_one(data)

    assert invalid_returns.index.tolist() == [3]


def test_validation_does_not_modify_input_data() -> None:
    """The validation layer must not silently clean the source table."""
    data = make_clean_panel()
    original = data.copy(deep=True)

    validate_panel_data(data)

    pd.testing.assert_frame_equal(data, original)
