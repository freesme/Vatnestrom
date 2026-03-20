"""
均值回归策略模块

基于价格偏离移动平均线的程度进行反向交易：
  - 价格低于均线 * (1 - threshold) → 买入（超跌回归）
  - 价格高于均线 * (1 + threshold) → 卖出（超涨回归）

参数说明:
  - ma_window: 移动平均线窗口，默认 20
  - threshold: 偏离阈值（百分比），默认 5.0（即 5%）
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""

    def generate_signals(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        ma_window = params.get("ma_window", 20)
        threshold = params.get("threshold", 5.0) / 100.0

        ma = vbt.MA.run(price, window=ma_window).ma

        entries = price < ma * (1 - threshold)
        exits = price > ma * (1 + threshold)

        return entries, exits

    def generate_indicators(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> list[dict]:
        ma_window = params.get("ma_window", 20)
        threshold = params.get("threshold", 5.0) / 100.0

        ma = vbt.MA.run(price, window=ma_window).ma
        upper = ma * (1 + threshold)
        lower = ma * (1 - threshold)

        return [
            {
                "name": f"MA{ma_window}",
                "color": "#9ca3af",
                "data": series_to_line_data(ma),
                "overlay": True,
            },
            {
                "name": "Upper",
                "color": "#ef4444",
                "data": series_to_line_data(upper),
                "overlay": True,
            },
            {
                "name": "Lower",
                "color": "#22c55e",
                "data": series_to_line_data(lower),
                "overlay": True,
            },
        ]
