"""
核心配置模块

定义回测所需的全部配置参数，使用 dataclass 提供默认值，
方便在 API 层和服务层之间传递统一的配置对象。
"""

from dataclasses import dataclass, field


@dataclass
class BacktestConfig:
    """回测配置数据类

    Attributes:
        symbol: 股票/资产代码，例如 "AAPL"（苹果）、"MSFT"（微软）
        start_date: 回测起始日期，格式 "YYYY-MM-DD"
        end_date: 回测结束日期，格式 "YYYY-MM-DD"
        init_cash: 初始资金（美元），默认 10 万
        fees: 每笔交易的手续费比例，0.001 表示 0.1%
        freq: 数据频率，"1D" 表示日线
        strategy: 策略名称，需与 STRATEGY_REGISTRY 中的键匹配
        strategy_params: 策略专属参数，不同策略有不同的参数结构
    """
    symbol: str = "AAPL"
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    init_cash: float = 10_000.0
    fees: float = 0.001
    freq: str = "1D"
    interval: str = "1d"
    strategy: str = "ma_cross"
    strategy_params: dict = field(default_factory=lambda: {
        "fast_window": 10,   # 快速均线窗口期（天数）
        "slow_window": 50,   # 慢速均线窗口期（天数）
    })


# interval (用户选择的K线周期) → vectorbt freq (用于年化指标计算)
_INTERVAL_TO_FREQ = {
    "1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min",
    "30m": "30min", "1h": "1h", "4h": "4h", "12h": "12h", "1d": "1D",
}


def interval_to_freq(interval: str) -> str:
    """将用户选择的 interval 转换为 vectorbt Portfolio 所需的 freq 字符串"""
    return _INTERVAL_TO_FREQ.get(interval, "1D")
