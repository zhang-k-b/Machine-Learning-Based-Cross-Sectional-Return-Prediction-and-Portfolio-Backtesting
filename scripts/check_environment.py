"""检查Python环境，并用模拟价格验证最基础的数据计算。"""

from importlib.metadata import version
from pathlib import Path
import os
import sys

# 将第三方库缓存放在项目内的忽略目录，避免写入受限的系统目录。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(PROJECT_ROOT / ".cache" / "matplotlib"),
)

import matplotlib
import numpy
import pandas as pd
import pyarrow
import pytest
import seaborn
import sklearn

# 让这个脚本可以直接从项目根目录运行并导入src中的代码。
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.returns import calculate_trailing_return


def create_sample_prices() -> pd.DataFrame:
    """创建仅用于环境检查的小型模拟价格表。"""
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-05", periods=7, freq="B"),
            "close": [100.0, 101.0, 102.0, 103.0, 104.0, 110.0, 108.0],
        }
    )


def print_environment_versions() -> None:
    """打印Python和本项目主要依赖的版本。"""
    print(f"Python: {sys.version.split()[0]}")
    packages = {
        "numpy": numpy.__version__,
        "pandas": pd.__version__,
        "matplotlib": matplotlib.__version__,
        "seaborn": seaborn.__version__,
        "scikit-learn": sklearn.__version__,
        "pyarrow": pyarrow.__version__,
        "pytest": pytest.__version__,
        "jupyter": version("jupyter"),
    }
    for package_name, package_version in packages.items():
        print(f"{package_name}: {package_version}")


def main() -> None:
    """运行版本、模拟数据和5日历史收益率检查。"""
    print_environment_versions()

    sample_prices = create_sample_prices()
    checked_prices = calculate_trailing_return(sample_prices, periods=5)

    expected_columns = {"date", "close", "return_5d"}
    missing_columns = expected_columns.difference(checked_prices.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise RuntimeError(f"计算结果缺少列：{missing_text}")
    if not checked_prices["date"].is_monotonic_increasing:
        raise RuntimeError("价格数据没有按日期从早到晚排列")
    if checked_prices["return_5d"].notna().sum() != 2:
        raise RuntimeError("5日收益率的有效结果数量不符合预期")

    print("\n模拟价格和5日历史收益率：")
    print(checked_prices.to_string(index=False))
    print("\n环境验证成功")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n环境验证失败：{error}", file=sys.stderr)
        raise SystemExit(1) from error
