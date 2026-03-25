"""
Twelve Data 数据源适配器

通过 Twelve Data REST API 获取美股/全球股票的实时和历史行情数据。
免费额度：800 次/天。需要设置环境变量 TWELVE_DATA_API_KEY。
"""

import logging
import os

import pandas as pd
import requests

from app.services.datasources.base import BaseDataSource

logger = logging.getLogger(__name__)

_API_URL = "https://api.twelvedata.com/time_series"

# 项目 interval → Twelve Data interval
_INTERVAL_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "1h",
    "4h": "4h",
    "1d": "1day",
}


class TwelveDataSource(BaseDataSource):
    """Twelve Data 数据源，支持美股实时当日数据"""

    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
        api_key = os.environ.get("TWELVE_DATA_API_KEY")
        if not api_key:
            raise ValueError(
                "需要设置环境变量 TWELVE_DATA_API_KEY（免费注册: https://twelvedata.com）"
            )

        td_interval = _INTERVAL_MAP.get(interval)
        if not td_interval:
            supported = list(_INTERVAL_MAP.keys())
            raise ValueError(
                f"Twelve Data 不支持 interval={interval}，可用: {supported}"
            )

        # 去除 A 股后缀（Twelve Data 用不同格式）
        td_symbol = symbol.strip().upper()

        logger.info(
            "twelvedata fetch | symbol=%s interval=%s period=%s~%s",
            td_symbol, td_interval, start, end,
        )

        resp = requests.get(
            _API_URL,
            params={
                "symbol": td_symbol,
                "interval": td_interval,
                "start_date": start,
                "end_date": end,
                "apikey": api_key,
                "outputsize": 5000,
                "format": "JSON",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        # 检查 API 错误
        if data.get("status") == "error":
            raise ValueError(f"Twelve Data API 错误: {data.get('message', str(data))}")

        values = data.get("values")
        if not values:
            raise ValueError(f"Twelve Data 未返回数据: {td_symbol}")

        # 构造 DataFrame
        records = pd.DataFrame(values)
        records["datetime"] = pd.to_datetime(records["datetime"])
        records = records.set_index("datetime")
        records = records.sort_index()

        df = pd.DataFrame({
            "open": pd.to_numeric(records["open"], errors="coerce"),
            "high": pd.to_numeric(records["high"], errors="coerce"),
            "low": pd.to_numeric(records["low"], errors="coerce"),
            "close": pd.to_numeric(records["close"], errors="coerce"),
            "volume": pd.to_numeric(records["volume"], errors="coerce"),
        })

        df = df.dropna()

        if df.empty:
            raise ValueError(
                f"Twelve Data 在 {start}~{end} 范围内无数据: {td_symbol}"
            )

        return df
