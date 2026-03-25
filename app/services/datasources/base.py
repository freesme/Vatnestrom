"""
数据源适配器抽象基类

所有数据源（Yahoo Finance、新浪财经等）都需要继承此基类，
实现 fetch_ohlcv 方法以提供统一的 OHLCV 数据接口。
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseDataSource(ABC):
    """数据源适配器抽象基类"""

    @abstractmethod
    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
        """获取 OHLCV 数据

        Args:
            symbol: 股票代码
            start: 起始日期，格式 "YYYY-MM-DD"
            end: 结束日期，格式 "YYYY-MM-DD"
            interval: K线周期，如 "1m", "5m", "1h", "1d"

        Returns:
            DataFrame，列: open, high, low, close, volume，索引为 DatetimeIndex
        """
        ...

    def fetch_price(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.Series:
        """获取收盘价序列（默认实现，子类可覆盖优化）"""
        df = self.fetch_ohlcv(symbol, start, end, interval)
        return df["close"].dropna()
