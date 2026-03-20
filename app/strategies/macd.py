"""
MACD 信号线交叉策略模块

基于 MACD 线与信号线的交叉关系判断趋势：
  - MACD 线上穿信号线时，产生买入信号
  - MACD 线下穿信号线时，产生卖出信号

参数说明:
  - fast_window: 快速 EMA 窗口期，默认 12
  - slow_window: 慢速 EMA 窗口期，默认 26
  - signal_window: 信号线窗口期，默认 9
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class MACDStrategy(BaseStrategy):
    """MACD 信号线交叉策略"""

    def generate_signals(self, price: pd.Series, params: dict) -> tuple[pd.Series, pd.Series]:
        fast_window = params.get("fast_window", 12)
        slow_window = params.get("slow_window", 26)
        signal_window = params.get("signal_window", 9)

        macd_ind = vbt.MACD.run(price, fast_window=fast_window, slow_window=slow_window,
                                signal_window=signal_window)

        # MACD 线上穿信号线 -> 买入
        entries = macd_ind.macd_crossed_above(macd_ind.signal)
        # MACD 线下穿信号线 -> 卖出
        exits = macd_ind.macd_crossed_below(macd_ind.signal)

        return entries, exits

    def generate_indicators(self, price: pd.Series, params: dict) -> list[dict]:
        fast_window = params.get("fast_window", 12)
        slow_window = params.get("slow_window", 26)
        signal_window = params.get("signal_window", 9)

        macd_ind = vbt.MACD.run(price, fast_window=fast_window, slow_window=slow_window,
                                signal_window=signal_window)

        return [
            {
                "name": "MACD",
                "color": "#3b82f6",
                "data": series_to_line_data(macd_ind.macd),
                "overlay": False,
            },
            {
                "name": "Signal",
                "color": "#ef4444",
                "data": series_to_line_data(macd_ind.signal),
                "overlay": False,
            },
        ]
