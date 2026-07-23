"""Demonstrate data-quality checks with two synthetic securities.

使用两只虚拟股票演示数据质量检查。
"""

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.validation import validate_panel_data


def create_clean_panel() -> pd.DataFrame:
    """Create a small, clean panel for method verification.

    创建用于方法验证的小型干净面板数据。
    """
    rows: list[dict[str, object]] = []
    for security_id, ticker, starting_price in (
        ("SEC001", "AAA", 100.0),
        ("SEC002", "BBB", 50.0),
    ):
        for day_number, date in enumerate(
            pd.date_range("2024-01-02", periods=3, freq="B")
        ):
            close_price = starting_price + day_number
            rows.append(
                {
                    "date": date,
                    "security_id": security_id,
                    "ticker": ticker,
                    "exchange_code": "NASDAQ",
                    "security_type": "COMMON_STOCK",
                    "open_raw": close_price - 0.25,
                    "close_raw": close_price,
                    "volume_raw": 1_000_000 + day_number * 10_000,
                    "total_return": 0.0 if day_number == 0 else 0.01,
                    "price_return": 0.0 if day_number == 0 else 0.01,
                    "shares_outstanding": 10_000_000,
                    "market_cap": close_price * 10_000_000,
                    "price_adjustment_factor": 1.0,
                    "delisting_return": None,
                    "delisting_code": None,
                    "trading_status": "ACTIVE",
                }
            )
    return pd.DataFrame(rows)


def create_problem_panel() -> pd.DataFrame:
    """Create a panel containing deliberate quality problems.

    创建故意包含重复、错误日期、负成交量和缺失价格的问题数据。
    """
    data = create_clean_panel().iloc[[1, 0, 0, 3, 4, 5]].copy()
    data = data.reset_index(drop=True)
    data["date"] = data["date"].astype(object)
    data.loc[3, "date"] = "not-a-date"
    data.loc[4, "volume_raw"] = -500
    data.loc[5, "close_raw"] = None
    data.loc[5, "total_return"] = -1.20
    return data


def print_report(title: str, report: dict[str, object]) -> None:
    """Print a concise bilingual validation summary.

    打印简洁的双语数据验证摘要。
    """
    print(f"\n{title}")
    print("=" * len(title))
    print(f"总体是否通过 / Overall valid: {report['is_valid']}")
    print(
        "重复主键行数 / Duplicate-key rows: "
        f"{len(report['duplicate_primary_key_rows'])}"
    )
    print(
        "错误日期行数 / Invalid-date rows: "
        f"{len(report['invalid_date_rows'])}"
    )
    print(
        "日期未排序证券 / Unsorted securities: "
        f"{report['unsorted_securities']}"
    )
    print(
        "非正价格行数 / Non-positive-price rows: "
        f"{len(report['non_positive_price_rows'])}"
    )
    print(
        "负成交量行数 / Negative-volume rows: "
        f"{len(report['negative_volume_rows'])}"
    )
    print(
        "低于-100%收益行数 / Returns below -100%: "
        f"{len(report['returns_below_minus_one_rows'])}"
    )
    print(
        "核心字段缺失 / Missing core fields: "
        f"{report['missing_core_field_counts']}"
    )
    print(
        "有效交易日 / Valid trading days: "
        f"{report['valid_trading_day_counts']}"
    )


def main() -> None:
    """Run clean and problematic synthetic-data demonstrations.

    运行干净数据与问题数据的模拟演示。
    """
    clean_panel = create_clean_panel()
    problem_panel = create_problem_panel()

    print("研究设计、数据字典与数据质量")
    print("Research Design, Data Dictionary, and Data Quality")
    print("\n说明：以下数据完全由程序构造，不是真实股票数据。")
    print("Note: The following data are synthetic, not real market data.")

    clean_report = validate_panel_data(clean_panel)
    problem_report = validate_panel_data(problem_panel)

    print_report("干净数据 / Clean panel", clean_report)
    print_report("问题数据 / Problem panel", problem_report)

    print("\n问题数据样例 / Problematic observations:")
    print(
        problem_panel[
            [
                "security_id",
                "date",
                "close_raw",
                "volume_raw",
                "total_return",
            ]
        ].to_string(index=False)
    )
    print("\n验证程序只报告问题，没有删除或填补任何观测。")
    print("The validator reports issues without deleting or imputing observations.")


if __name__ == "__main__":
    main()
