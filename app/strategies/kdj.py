"""
KDJ 随机指标策略模块

基于 Stochastic 指标的 %K/%D 交叉判断超买超卖：
  - %K 上穿 %D 且处于超卖区 → 买入
  - %K 下穿 %D 且处于超买区 → 卖出

参数说明:
  - k_window: %K 计算窗口，默认 9
  - d_window: %D 平滑窗口，默认 3
  - oversold: 超卖阈值，默认 20
  - overbought: 超买阈值，默认 80
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class KDJStrategy(BaseStrategy):
    """KDJ 随机指标策略"""

    def generate_signals(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        k_window = params.get("k_window", 9)
        d_window = params.get("d_window", 3)
        oversold = params.get("oversold", 20)
        overbought = params.get("overbought", 80)

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        stoch = vbt.STOCH.run(high, low, price, k_window=k_window, d_ewm=False, d_window=d_window)
        k = stoch.percent_k
        d = stoch.percent_d

        # K 上穿 D 且 K < oversold → 买入
        k_cross_above_d = stoch.percent_k_crossed_above(d)
        entries = k_cross_above_d & (k < oversold)

        # K 下穿 D 且 K > overbought → 卖出
        k_cross_below_d = stoch.percent_k_crossed_below(d)
        exits = k_cross_below_d & (k > overbought)

        return entries, exits

    def generate_indicators(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> list[dict]:
        k_window = params.get("k_window", 9)
        d_window = params.get("d_window", 3)

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        stoch = vbt.STOCH.run(high, low, price, k_window=k_window, d_ewm=False, d_window=d_window)

        return [
            {
                "name": "%K",
                "color": "#f59e0b",
                "data": series_to_line_data(stoch.percent_k),
                "overlay": False,
            },
            {
                "name": "%D",
                "color": "#8b5cf6",
                "data": series_to_line_data(stoch.percent_d),
                "overlay": False,
            },
        ]
