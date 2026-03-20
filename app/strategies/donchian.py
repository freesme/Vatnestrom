"""
海龟突破（Donchian Channel）策略模块

基于唐奇安通道判断价格突破：
  - 价格突破 entry_window 日最高价时，产生买入信号
  - 价格跌破 exit_window 日最低价时，产生卖出信号

参数说明:
  - entry_window: 入场通道窗口期，默认 20 天
  - exit_window: 出场通道窗口期，默认 10 天
"""

import pandas as pd

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class DonchianStrategy(BaseStrategy):
    """海龟突破（Donchian Channel）策略"""

    def generate_signals(self, price: pd.Series, params: dict) -> tuple[pd.Series, pd.Series]:
        entry_window = params.get("entry_window", 20)
        exit_window = params.get("exit_window", 10)

        upper = price.rolling(entry_window).max()
        lower = price.rolling(exit_window).min()

        # 价格突破入场通道上轨 -> 买入
        entries = price >= upper.shift(1)
        # 价格跌破出场通道下轨 -> 卖出
        exits = price <= lower.shift(1)

        return entries, exits

    def generate_indicators(self, price: pd.Series, params: dict) -> list[dict]:
        entry_window = params.get("entry_window", 20)
        exit_window = params.get("exit_window", 10)

        upper = price.rolling(entry_window).max()
        lower = price.rolling(exit_window).min()

        return [
            {
                "name": f"Upper({entry_window})",
                "color": "#ef4444",
                "data": series_to_line_data(upper),
                "overlay": True,
            },
            {
                "name": f"Lower({exit_window})",
                "color": "#22c55e",
                "data": series_to_line_data(lower),
                "overlay": True,
            },
        ]
