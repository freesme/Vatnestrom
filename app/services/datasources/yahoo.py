"""
Yahoo Finance 数据源适配器

通过 vectorbt 的 YFData 接口下载历史行情数据。
支持原生 interval 和需要 resample 的自定义 interval。
"""

import pandas as pd
import vectorbt as vbt

from app.services.datasources.base import BaseDataSource

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


class YahooDataSource(BaseDataSource):
    """Yahoo Finance 数据源"""

    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
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
