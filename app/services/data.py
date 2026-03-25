"""
数据获取服务模块

负责从外部数据源（Yahoo Finance）下载历史行情数据。
后续可扩展支持更多数据源（如 Binance、Tushare 等），
只需在此模块中添加新的获取函数即可。
"""

import pandas as pd
import vectorbt as vbt

# yfinance 原生支持的 interval
_NATIVE_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d"}

# 需要 resample 的 interval → (下载用的源 interval, resample 规则)
_RESAMPLE_MAP = {
    "3m":  ("1m",  "3min"),
    "4h":  ("1h",  "4h"),
    "12h": ("1h",  "12h"),
}


def _resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """将 OHLCV DataFrame 按指定规则聚合"""
    return df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna()


def fetch_price(symbol: str, start: str, end: str, interval: str = "1d") -> pd.Series:
    """从 Yahoo Finance 下载指定股票的收盘价数据

    Args:
        symbol: 股票代码，例如 "AAPL"（苹果）、"TSLA"（特斯拉）
        start: 起始日期，格式 "YYYY-MM-DD"
        end: 结束日期，格式 "YYYY-MM-DD"
        interval: K线周期，如 "1m", "5m", "1h", "1d" 等

    Returns:
        收盘价的 pandas Series，索引为交易日期/时间
    """
    df = fetch_ohlcv(symbol, start, end, interval)
    return df["close"].dropna()


def fetch_ohlcv(symbol: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    """从 Yahoo Finance 下载指定股票的完整 OHLCV 数据

    支持原生 interval（1m, 5m, 15m, 30m, 1h, 1d 等）和需要 resample 的
    interval（3m, 4h, 12h）。

    Args:
        symbol: 股票代码，例如 "AAPL"（苹果）、"TSLA"（特斯拉）
        start: 起始日期，格式 "YYYY-MM-DD"
        end: 结束日期，格式 "YYYY-MM-DD"
        interval: K线周期

    Returns:
        包含 open/high/low/close/volume 列的 DataFrame
    """
    # 确定实际下载用的 interval 和可能的 resample 规则
    resample_rule = None
    download_interval = interval
    if interval in _RESAMPLE_MAP:
        download_interval, resample_rule = _RESAMPLE_MAP[interval]

    data = vbt.YFData.download(symbol, start=start, end=end, interval=download_interval)

    df = pd.DataFrame({
        "open": data.get("Open"),
        "high": data.get("High"),
        "low": data.get("Low"),
        "close": data.get("Close"),
        "volume": data.get("Volume"),
    })

    df = df.dropna()

    if resample_rule:
        df = _resample_ohlcv(df, resample_rule)

    return df
