"""
ATR 通道突破策略模块

基于 ATR（真实波幅均值）构建自适应通道：
  - 价格上穿均线 + multiplier * ATR → 买入（波动率突破）
  - 价格下穿均线 - multiplier * ATR → 卖出

参数说明:
  - atr_window: ATR 计算窗口，默认 14
  - ma_window: 中轨均线窗口，默认 20
  - multiplier: ATR 通道倍数，默认 2.0
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class ATRChannelStrategy(BaseStrategy):
    """ATR 通道突破策略"""

    def generate_signals(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        atr_window = params.get("atr_window", 14)
        ma_window = params.get("ma_window", 20)
        multiplier = params.get("multiplier", 2.0)

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        atr = vbt.ATR.run(high, low, price, window=atr_window).atr
        ma = vbt.MA.run(price, window=ma_window).ma

        upper = ma + multiplier * atr
        lower = ma - multiplier * atr

        entries = price.vbt.crossed_above(upper)
        exits = price.vbt.crossed_below(lower)

        return entries, exits

    def generate_indicators(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> list[dict]:
        atr_window = params.get("atr_window", 14)
        ma_window = params.get("ma_window", 20)
        multiplier = params.get("multiplier", 2.0)

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        atr = vbt.ATR.run(high, low, price, window=atr_window).atr
        ma = vbt.MA.run(price, window=ma_window).ma

        upper = ma + multiplier * atr
        lower = ma - multiplier * atr

        return [
            {
                "name": "Mid",
                "color": "#9ca3af",
                "data": series_to_line_data(ma),
                "overlay": True,
            },
            {
                "name": "ATR Upper",
                "color": "#ef4444",
                "data": series_to_line_data(upper),
                "overlay": True,
            },
            {
                "name": "ATR Lower",
                "color": "#22c55e",
                "data": series_to_line_data(lower),
                "overlay": True,
            },
        ]

    def generate_tp_sl(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        atr_window = params.get("atr_window", 14)
        multiplier = params.get("multiplier", 2.0)

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        atr = vbt.ATR.run(high, low, price, window=atr_window).atr

        tp_pct = (multiplier * atr / price).clip(0.001, 0.5)
        sl_pct = (multiplier * atr / price).clip(0.001, 0.5)
        return tp_pct, sl_pct
