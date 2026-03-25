"""
数据获取服务模块（代理层）

统一数据获取入口，根据 source 参数分发到对应的数据源适配器。
支持的数据源在 app/services/datasources/__init__.py 中注册。
"""

import pandas as pd

from app.services.datasources import get_datasource


def fetch_price(
    symbol: str, start: str, end: str, interval: str = "1d", source: str = "tickflow"
) -> pd.Series:
    """获取收盘价序列

    Args:
        symbol: 股票代码
        start: 起始日期
        end: 结束日期
        interval: K线周期
        source: 数据源名称（yahoo / sina）

    Returns:
        收盘价的 pandas Series
    """
    ds = get_datasource(source)
    return ds.fetch_price(symbol, start, end, interval)


def fetch_ohlcv(
    symbol: str, start: str, end: str, interval: str = "1d", source: str = "tickflow"
) -> pd.DataFrame:
    """获取完整 OHLCV 数据

    Args:
        symbol: 股票代码
        start: 起始日期
        end: 结束日期
        interval: K线周期
        source: 数据源名称（yahoo / sina）

    Returns:
        包含 open/high/low/close/volume 列的 DataFrame
    """
    ds = get_datasource(source)
    return ds.fetch_ohlcv(symbol, start, end, interval)
