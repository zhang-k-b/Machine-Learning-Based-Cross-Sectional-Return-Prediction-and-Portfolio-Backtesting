"""项目的基础配置。"""

from pathlib import Path


# 项目根目录：根据当前文件的位置自动确定。
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 原始数据目录：保存下载后未经修改的数据。
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# 处理后数据目录：保存清洗和对齐后的研究数据。
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# 图片输出目录：保存收益曲线和回撤图等图片。
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

# 表格输出目录：保存模型指标和回测结果表格。
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

# 随机种子：保证可重复的随机实验尽量得到相同结果。
RANDOM_SEED = 42

# 预测周期：预测未来5个交易日的收益。
FORECAST_HORIZON_DAYS = 5

# 年交易日数量：用于把日频指标换算成年化指标。
TRADING_DAYS_PER_YEAR = 252

# 单边手续费率：每次买入或卖出按成交金额的0.03%计算。
COMMISSION_RATE = 0.0003

# 单边滑点率：每次买入或卖出按成交金额的0.05%估计。
SLIPPAGE_RATE = 0.0005
