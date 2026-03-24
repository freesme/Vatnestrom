"""
策略注册与发现模块

所有策略都需要在 STRATEGY_REGISTRY 中注册。
扩展新策略时，只需:
  1. 在 strategies/ 目录下新建策略文件，继承 BaseStrategy
  2. 在此处导入并添加到 STRATEGY_REGISTRY 字典中
"""

from app.strategies.atr_channel import ATRChannelStrategy
from app.strategies.bollinger import BollingerStrategy
from app.strategies.donchian import DonchianStrategy
from app.strategies.kdj import KDJStrategy
from app.strategies.ma_cross import MACrossStrategy
from app.strategies.macd import MACDStrategy
from app.strategies.mean_reversion import MeanReversionStrategy
from app.strategies.rsi import RSIStrategy
from app.strategies.supertrend import SuperTrendStrategy

# 策略注册表：策略名称 -> 策略类
# API 请求中通过 strategy 字段指定名称来选择策略
STRATEGY_REGISTRY: dict[str, type] = {
    "ma_cross": MACrossStrategy,
    "rsi": RSIStrategy,
    "bollinger": BollingerStrategy,
    "macd": MACDStrategy,
    "donchian": DonchianStrategy,
    "kdj": KDJStrategy,
    "mean_reversion": MeanReversionStrategy,
    "atr_channel": ATRChannelStrategy,
    "supertrend": SuperTrendStrategy,
}


def get_strategy(name: str):
    """根据策略名称获取策略实例

    Args:
        name: 策略名称，必须是 STRATEGY_REGISTRY 中已注册的键

    Returns:
        对应策略类的实例

    Raises:
        ValueError: 当策略名称未注册时抛出，并提示可用的策略列表
    """
    cls = STRATEGY_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGY_REGISTRY.keys())}")
    return cls()
