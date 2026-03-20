"""
布林带突破策略模块

基于布林带（Bollinger Bands）判断价格突破：
  - 价格下穿下轨时，产生买入信号
  - 价格上穿上轨时，产生卖出信号

参数说明:
  - bb_window: 布林带计算窗口期，默认 20 天
  - bb_std: 标准差倍数，默认 2.0
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class BollingerStrategy(BaseStrategy):
    """布林带突破策略"""

    def generate_signals(self, price: pd.Series, params: dict) -> tuple[pd.Series, pd.Series]:
        bb_window = params.get("bb_window", 20)
        bb_std = params.get("bb_std", 2.0)

        bb = vbt.BBANDS.run(price, window=bb_window, ewm=False, alpha=bb_std)

        # 价格下穿下轨 -> 买入
        entries = price.vbt.crossed_below(bb.lower)
        # 价格上穿上轨 -> 卖出
        exits = price.vbt.crossed_above(bb.upper)

        return entries, exits

    def generate_indicators(self, price: pd.Series, params: dict) -> list[dict]:
        bb_window = params.get("bb_window", 20)
        bb_std = params.get("bb_std", 2.0)

        bb = vbt.BBANDS.run(price, window=bb_window, ewm=False, alpha=bb_std)

        return [
            {
                "name": "Upper Band",
                "color": "#ef4444",
                "data": series_to_line_data(bb.upper),
            },
            {
                "name": "Middle Band",
                "color": "#9ca3af",
                "data": series_to_line_data(bb.middle),
            },
            {
                "name": "Lower Band",
                "color": "#22c55e",
                "data": series_to_line_data(bb.lower),
            },
        ]
