"""Basic validation for daily security panel data.

日频证券面板数据的基础验证工具。
"""

from collections.abc import Sequence

import pandas as pd


REQUIRED_COLUMNS: tuple[str, ...] = (
    "security_id",
    "date",
    "close_raw",
    "volume_raw",
    "total_return",
)

CORE_FIELDS: tuple[str, ...] = (
    "security_id",
    "date",
    "close_raw",
    "volume_raw",
    "total_return",
)


def check_required_columns(
    data: pd.DataFrame,
    required_columns: Sequence[str] = REQUIRED_COLUMNS,
) -> None:
    """Raise a clear error when required fields are missing.

    当必要字段缺失时给出清楚错误，不修改原始数据。
    """
    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(
            f"缺少必要字段 / Missing required columns: {missing_text}"
        )


def find_duplicate_primary_keys(
    data: pd.DataFrame,
    key_columns: Sequence[str] = ("security_id", "date"),
) -> pd.DataFrame:
    """Return every row involved in a duplicated primary key.

    返回所有涉及重复主键的行，但不自动删除。
    """
    check_required_columns(data, key_columns)
    duplicate_mask = data.duplicated(subset=list(key_columns), keep=False)
    return data.loc[duplicate_mask].copy()


def find_invalid_dates(
    data: pd.DataFrame,
    date_column: str = "date",
) -> pd.DataFrame:
    """Return rows whose dates cannot be parsed.

    返回日期无法解析的行，但不替换错误日期。
    """
    check_required_columns(data, (date_column,))
    parsed_dates = pd.to_datetime(
        data[date_column],
        errors="coerce",
        format="mixed",
    )
    return data.loc[parsed_dates.isna()].copy()


def find_unsorted_securities(
    data: pd.DataFrame,
    security_column: str = "security_id",
    date_column: str = "date",
) -> list[str]:
    """List securities whose valid dates are not in chronological order.

    列出内部有效日期没有按时间先后排列的证券。
    """
    check_required_columns(data, (security_column, date_column))
    parsed_dates = pd.to_datetime(
        data[date_column],
        errors="coerce",
        format="mixed",
    )

    unsorted_securities: list[str] = []
    for security_id, group in data.groupby(security_column, sort=False):
        valid_dates = parsed_dates.loc[group.index].dropna()
        if not valid_dates.is_monotonic_increasing:
            unsorted_securities.append(str(security_id))
    return unsorted_securities


def find_non_positive_prices(
    data: pd.DataFrame,
    price_columns: Sequence[str] = ("open_raw", "close_raw"),
) -> pd.DataFrame:
    """Return rows containing zero or negative non-missing prices.

    返回含零价格或负价格的行，但不修正价格。
    """
    available_columns = [
        column for column in price_columns if column in data.columns
    ]
    if not available_columns:
        raise ValueError(
            "没有可检查的价格字段 / No requested price columns are available"
        )

    invalid_mask = pd.Series(False, index=data.index)
    for column in available_columns:
        numeric_values = pd.to_numeric(data[column], errors="coerce")
        invalid_mask |= numeric_values.notna() & (numeric_values <= 0)
    return data.loc[invalid_mask].copy()


def find_negative_volumes(
    data: pd.DataFrame,
    volume_column: str = "volume_raw",
) -> pd.DataFrame:
    """Return rows containing negative trading volume.

    返回成交量小于零的行；零成交量本身不视为负值错误。
    """
    check_required_columns(data, (volume_column,))
    numeric_volume = pd.to_numeric(data[volume_column], errors="coerce")
    return data.loc[numeric_volume.notna() & (numeric_volume < 0)].copy()


def find_returns_below_minus_one(
    data: pd.DataFrame,
    return_columns: Sequence[str] = ("total_return", "price_return"),
) -> pd.DataFrame:
    """Return rows containing simple returns below negative 100 percent.

    返回简单收益率低于-100%的行，但不自动删除极端值。
    """
    available_columns = [
        column for column in return_columns if column in data.columns
    ]
    if not available_columns:
        raise ValueError(
            "没有可检查的收益率字段 / No requested return columns are available"
        )

    invalid_mask = pd.Series(False, index=data.index)
    for column in available_columns:
        numeric_values = pd.to_numeric(data[column], errors="coerce")
        invalid_mask |= numeric_values.notna() & (numeric_values < -1)
    return data.loc[invalid_mask].copy()


def count_missing_core_fields(
    data: pd.DataFrame,
    core_fields: Sequence[str] = CORE_FIELDS,
) -> dict[str, int]:
    """Count missing observations in each core field.

    统计每个核心字段的缺失观测数量。
    """
    check_required_columns(data, core_fields)
    missing_counts = data.loc[:, list(core_fields)].isna().sum()
    return {
        str(column): int(count)
        for column, count in missing_counts.items()
    }


def count_valid_trading_days(
    data: pd.DataFrame,
    security_column: str = "security_id",
    date_column: str = "date",
    price_column: str = "close_raw",
    volume_column: str = "volume_raw",
) -> dict[str, int]:
    """Count unique valid trading dates for each security.

    统计每只证券具有有效日期、正价格和非负成交量的唯一交易日数量。
    """
    required = (
        security_column,
        date_column,
        price_column,
        volume_column,
    )
    check_required_columns(data, required)

    parsed_dates = pd.to_datetime(
        data[date_column],
        errors="coerce",
        format="mixed",
    )
    numeric_prices = pd.to_numeric(data[price_column], errors="coerce")
    numeric_volumes = pd.to_numeric(data[volume_column], errors="coerce")

    valid_mask = (
        data[security_column].notna()
        & parsed_dates.notna()
        & numeric_prices.notna()
        & (numeric_prices > 0)
        & numeric_volumes.notna()
        & (numeric_volumes >= 0)
    )

    valid_rows = pd.DataFrame(
        {
            "security_id": data.loc[valid_mask, security_column].astype(str),
            "date": parsed_dates.loc[valid_mask],
        }
    ).drop_duplicates()
    valid_counts = valid_rows.groupby("security_id")["date"].nunique()

    all_security_ids = (
        data.loc[data[security_column].notna(), security_column]
        .astype(str)
        .drop_duplicates()
    )
    return {
        security_id: int(valid_counts.get(security_id, 0))
        for security_id in all_security_ids
    }


def validate_panel_data(data: pd.DataFrame) -> dict[str, object]:
    """Run all basic checks and return a report without changing the input.

    运行全部基础检查并返回报告，不修改、删除或填补输入数据。
    """
    check_required_columns(data)

    duplicate_rows = find_duplicate_primary_keys(data)
    invalid_dates = find_invalid_dates(data)
    unsorted_securities = find_unsorted_securities(data)
    non_positive_prices = find_non_positive_prices(data)
    negative_volumes = find_negative_volumes(data)
    invalid_returns = find_returns_below_minus_one(data)
    missing_core_fields = count_missing_core_fields(data)
    valid_trading_days = count_valid_trading_days(data)

    is_valid = (
        duplicate_rows.empty
        and invalid_dates.empty
        and not unsorted_securities
        and non_positive_prices.empty
        and negative_volumes.empty
        and invalid_returns.empty
        and sum(missing_core_fields.values()) == 0
    )

    return {
        "is_valid": bool(is_valid),
        "duplicate_primary_key_rows": duplicate_rows,
        "invalid_date_rows": invalid_dates,
        "unsorted_securities": unsorted_securities,
        "non_positive_price_rows": non_positive_prices,
        "negative_volume_rows": negative_volumes,
        "returns_below_minus_one_rows": invalid_returns,
        "missing_core_field_counts": missing_core_fields,
        "valid_trading_day_counts": valid_trading_days,
    }
