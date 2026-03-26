"""
策略基类模块

定义所有交易策略必须实现的接口。
新策略需继承 BaseStrategy 并实现 generate_signals 和 generate_indicators 方法。
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    """交易策略抽象基类

    所有自定义策略都必须继承此类，并实现 generate_signals 方法。
    可选实现 generate_indicators 方法，用于在图表上叠加显示技术指标线。
    """

    @abstractmethod
    def generate_signals(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        """根据价格数据和参数生成交易信号

        Args:
            price: 收盘价时间序列（pandas Series，索引为日期）
            params: 策略参数字典，由各策略自行定义所需的键值
            ohlcv: 完整的 OHLCV DataFrame（可选，需要 high/low 的策略使用）

        Returns:
            一个元组 (entries, exits)：
            - entries: 买入信号，布尔型 Series，True 表示该时刻触发买入
            - exits:   卖出信号，布尔型 Series，True 表示该时刻触发卖出
        """
        ...

    def generate_indicators(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> list[dict]:
        """生成策略对应的技术指标线数据，用于在图表上叠加显示

        默认返回空列表（无指标线）。子类可覆写此方法，返回需要展示的指标线。

        Args:
            price: 收盘价时间序列
            params: 策略参数字典
            ohlcv: 完整的 OHLCV DataFrame（可选）

        Returns:
            指标线列表，每条指标线为一个字典：
            {
                "name": "MA5",          # 指标名称，显示在图例中
                "color": "#f59e0b",     # 线条颜色
                "data": [               # 数据点列表
                    {"time": "2024-01-02", "value": 150.25},
                    ...
                ]
            }
        """
        return []

    def generate_tp_sl(
        self, price: pd.Series, params: dict, ohlcv: pd.DataFrame | None = None
    ) -> tuple[pd.Series, pd.Series]:
        """根据当前指标计算止盈和止损百分比

        默认返回固定百分比（止盈 5%、止损 3%）。子类可覆写此方法，
        基于各自的技术指标动态计算每根 K 线对应的止盈止损比例。

        Args:
            price: 收盘价时间序列
            params: 策略参数字典
            ohlcv: 完整的 OHLCV DataFrame（可选）

        Returns:
            一个元组 (tp_pct, sl_pct)：
            - tp_pct: 止盈百分比 Series，值域 [0.001, 0.5]，如 0.05 表示 5%
            - sl_pct: 止损百分比 Series，值域 [0.001, 0.5]，如 0.03 表示 3%
        """
        tp_pct = pd.Series(0.05, index=price.index)
        sl_pct = pd.Series(0.03, index=price.index)
        return tp_pct, sl_pct
