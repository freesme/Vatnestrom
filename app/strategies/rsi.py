"""
RSI 超买超卖策略模块

基于相对强弱指数（RSI）判断市场超买超卖状态：
  - RSI 低于 oversold 阈值时，产生买入信号
  - RSI 高于 overbought 阈值时，产生卖出信号

参数说明:
  - rsi_window: RSI 计算窗口期，默认 14 天
  - oversold: 超卖阈值，默认 30
  - overbought: 超买阈值，默认 70
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class RSIStrategy(BaseStrategy):
    """RSI 超买超卖策略"""

    def generate_signals(self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None) -> tuple[pd.Series, pd.Series]:
        rsi_window = params.get("rsi_window", 14)
        oversold = params.get("oversold", 30)
        overbought = params.get("overbought", 70)

        rsi = vbt.RSI.run(price, window=rsi_window)
        rsi_values = rsi.rsi

        entries = rsi_values < oversold
        exits = rsi_values > overbought

        return entries, exits

    def generate_indicators(self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None) -> list[dict]:
        rsi_window = params.get("rsi_window", 14)

        rsi = vbt.RSI.run(price, window=rsi_window)

        return [
            {
                "name": f"RSI{rsi_window}",
                "color": "#8b5cf6",
                "data": series_to_line_data(rsi.rsi),
                "overlay": False,
            },
        ]
