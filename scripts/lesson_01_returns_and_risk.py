"""Demonstrate return, compounding, and risk calculations with synthetic data.

使用模拟数据演示收益率、复利和风险计算。
"""

from pathlib import Path
import os
import sys

# Keep Matplotlib's cache inside the ignored project cache directory.
# 将Matplotlib缓存放在项目内已忽略的缓存目录。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(PROJECT_ROOT / ".cache" / "matplotlib"),
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import FIGURES_DIR
from src.evaluation.return_metrics import (
    calculate_annualized_volatility,
    calculate_daily_returns,
    calculate_wealth_index,
)


def create_synthetic_prices() -> pd.DataFrame:
    """Create a small price table for learning and method verification.

    创建用于学习和方法验证的小型模拟价格表。
    """
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-05", periods=6, freq="B"),
            "close": [100.0, 102.0, 101.0, 105.0, 104.0, 108.0],
        }
    )


def save_learning_figure(results: pd.DataFrame, output_path: Path) -> None:
    """Save price and cumulative wealth charts.

    保存价格与累计财富曲线。
    """
    figure, axes = plt.subplots(nrows=2, ncols=1, figsize=(9, 7), sharex=True)

    axes[0].plot(results["date"], results["close"], marker="o", color="#1f77b4")
    axes[0].set_title("Synthetic Closing Price")
    axes[0].set_ylabel("Price")
    axes[0].grid(alpha=0.3)

    axes[1].plot(
        results["date"],
        results["wealth_index"],
        marker="o",
        color="#2ca02c",
    )
    axes[1].axhline(1.0, color="#666666", linestyle="--", linewidth=1)
    axes[1].set_title("Cumulative Wealth from an Initial Value of 1.0")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Wealth Index")
    axes[1].grid(alpha=0.3)

    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    """Run the bilingual lesson demonstration.

    运行双语课程演示。
    """
    prices = create_synthetic_prices()
    results = calculate_daily_returns(prices)
    results["wealth_index"] = calculate_wealth_index(
        results["simple_return"],
        initial_wealth=1.0,
    )
    annualized_volatility = calculate_annualized_volatility(
        results["simple_return"]
    )

    output_path = FIGURES_DIR / "01_return_and_risk_basics.png"
    save_learning_figure(results, output_path)

    print("收益率、复利与风险基础 / Return, Compounding, and Risk Fundamentals")
    print("\n模拟结果 / Synthetic results:")
    print(results.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
    print(
        "\n年化波动率 / Annualized volatility: "
        f"{annualized_volatility:.2%}"
    )
    print(f"图表已保存 / Figure saved to: {output_path}")
    print(
        "\n方法说明 / Method note: "
        "Each return uses only the current and previous prices."
    )
    print("每个收益率只使用当期价格和前一期价格。")


if __name__ == "__main__":
    main()
