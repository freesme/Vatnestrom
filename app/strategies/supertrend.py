"""
SuperTrend 超级趋势策略模块（基于 pandas-ta）

SuperTrend 是一种趋势跟踪指标，基于 ATR 动态调整支撑/阻力线：
  - 方向由 1 变为 -1（趋势转空）→ 卖出
  - 方向由 -1 变为 1（趋势转多）→ 买入

参数说明:
  - st_length: SuperTrend 周期，默认 10
  - st_multiplier: ATR 通道倍数，默认 3.0
"""

import pandas as pd
import pandas_ta

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class SuperTrendStrategy(BaseStrategy):
    """SuperTrend 超级趋势策略（pandas-ta 示例）"""

    def _compute(self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None):
        length = int(params.get("st_length", 10))
        multiplier = float(params.get("st_multiplier", 3.0))

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        st = pandas_ta.supertrend(high, low, price, length=length, multiplier=multiplier)

        col_prefix = f"_{length}_{multiplier}"
        trend_line = st[f"SUPERT{col_prefix}"]
        direction = st[f"SUPERTd{col_prefix}"]
        long_line = st[f"SUPERTl{col_prefix}"]
        short_line = st[f"SUPERTs{col_prefix}"]

        return trend_line, direction, long_line, short_line

    def generate_signals(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        _, direction, _, _ = self._compute(price, params, ohlcv)

        # 方向从 -1 变为 1 → 买入；从 1 变为 -1 → 卖出
        prev_dir = direction.shift(1)
        entries = (prev_dir == -1) & (direction == 1)
        exits = (prev_dir == 1) & (direction == -1)

        return entries.fillna(False), exits.fillna(False)

    def generate_indicators(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> list[dict]:
        _, _, long_line, short_line = self._compute(price, params, ohlcv)

        return [
            {
                "name": "SuperTrend Long",
                "color": "#22c55e",
                "data": series_to_line_data(long_line),
                "overlay": True,
            },
            {
                "name": "SuperTrend Short",
                "color": "#ef4444",
                "data": series_to_line_data(short_line),
                "overlay": True,
            },
        ]

    def generate_tp_sl(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        length = int(params.get("st_length", 10))
        multiplier = float(params.get("st_multiplier", 3.0))

        high = ohlcv["high"] if ohlcv is not None else price
        low = ohlcv["low"] if ohlcv is not None else price

        atr = pandas_ta.atr(high, low, price, length=length)

        tp_pct = (multiplier * atr / price).clip(0.001, 0.5)
        sl_pct = (multiplier * atr / price).clip(0.001, 0.5)
        return tp_pct, sl_pct
