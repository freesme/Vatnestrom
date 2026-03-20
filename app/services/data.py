"""
数据获取服务模块

负责从外部数据源（Yahoo Finance）下载历史行情数据。
后续可扩展支持更多数据源（如 Binance、Tushare 等），
只需在此模块中添加新的获取函数即可。
"""

import pandas as pd
import vectorbt as vbt


def fetch_price(symbol: str, start: str, end: str) -> pd.Series:
    """从 Yahoo Finance 下载指定股票的收盘价数据

    Args:
        symbol: 股票代码，例如 "AAPL"（苹果）、"TSLA"（特斯拉）
        start: 起始日期，格式 "YYYY-MM-DD"
        end: 结束日期，格式 "YYYY-MM-DD"

    Returns:
        收盘价的 pandas Series，索引为交易日期
    """
    # 通过 vectorbt 封装的 YFData 接口下载数据
    data = vbt.YFData.download(symbol, start=start, end=end)
    # 提取收盘价列
    return data.get("Close")


def fetch_ohlcv(symbol: str, start: str, end: str) -> pd.DataFrame:
    """从 Yahoo Finance 下载指定股票的完整 OHLCV 数据

    OHLCV = Open（开盘价）、High（最高价）、Low（最低价）、
            Close（收盘价）、Volume（成交量）

    Args:
        symbol: 股票代码，例如 "AAPL"（苹果）、"TSLA"（特斯拉）
        start: 起始日期，格式 "YYYY-MM-DD"
        end: 结束日期，格式 "YYYY-MM-DD"

    Returns:
        包含 open/high/low/close/volume 列的 DataFrame，索引为交易日期
    """
    data = vbt.YFData.download(symbol, start=start, end=end)

    # 将各列提取出来，组装成统一的 DataFrame
    df = pd.DataFrame({
        "open": data.get("Open"),
        "high": data.get("High"),
        "low": data.get("Low"),
        "close": data.get("Close"),
        "volume": data.get("Volume"),
    })

    return df
