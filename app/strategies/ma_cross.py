"""
双均线交叉策略模块

经典的趋势跟踪策略：
  - 当快速均线（短周期）上穿慢速均线（长周期）时，产生买入信号（金叉）
  - 当快速均线下穿慢速均线时，产生卖出信号（死叉）

参数说明:
  - fast_window: 快速均线的计算窗口期，默认 10 天
  - slow_window: 慢速均线的计算窗口期，默认 50 天
"""

import pandas as pd
import vectorbt as vbt

from app.strategies.base import BaseStrategy
from app.strategies.utils import series_to_line_data


class MACrossStrategy(BaseStrategy):
    """双均线交叉策略

    利用 vectorbt 内置的 MA 指标计算两条不同周期的移动平均线，
    通过交叉关系判断趋势方向，生成买卖信号。
    """

    def generate_signals(self, price: pd.Series, params: dict) -> tuple[pd.Series, pd.Series]:
        """生成均线交叉的买卖信号

        Args:
            price: 收盘价序列
            params: 必须包含 fast_window（快线周期）和 slow_window（慢线周期）

        Returns:
            (entries, exits) 买入和卖出的布尔信号序列
        """
        fast_window = params.get("fast_window", 10)
        slow_window = params.get("slow_window", 50)

        # 使用 vectorbt 计算两条移动平均线
        fast_ma = vbt.MA.run(price, window=fast_window)
        slow_ma = vbt.MA.run(price, window=slow_window)

        # 金叉：快线从下方穿越慢线 -> 买入信号
        entries = fast_ma.ma_crossed_above(slow_ma)
        # 死叉：快线从上方穿越慢线 -> 卖出信号
        exits = fast_ma.ma_crossed_below(slow_ma)

        return entries, exits

    def generate_indicators(self, price: pd.Series, params: dict) -> list[dict]:
        """生成快慢两条均线的指标数据，用于在 K 线图上叠加显示

        Args:
            price: 收盘价序列
            params: 包含 fast_window 和 slow_window

        Returns:
            两条均线的指标线数据（橙色快线、蓝色慢线）
        """
        fast_window = params.get("fast_window", 10)
        slow_window = params.get("slow_window", 50)

        fast_ma = vbt.MA.run(price, window=fast_window)
        slow_ma = vbt.MA.run(price, window=slow_window)

        return [
            {
                "name": f"MA{fast_window}",
                "color": "#f59e0b",
                "data": series_to_line_data(fast_ma.ma),
                "overlay": True,
            },
            {
                "name": f"MA{slow_window}",
                "color": "#3b82f6",
                "data": series_to_line_data(slow_ma.ma),
                "overlay": True,
            },
        ]
