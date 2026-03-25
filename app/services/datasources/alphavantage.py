"""
Alpha Vantage 数据源适配器

通过 Alpha Vantage REST API 获取美股历史和当日行情数据。
免费额度：25 次/天，数据延迟 15 分钟。需要设置环境变量 ALPHA_VANTAGE_API_KEY。
"""

import logging
import os

import pandas as pd
import requests

from app.services.datasources.base import BaseDataSource

logger = logging.getLogger(__name__)

_API_URL = "https://www.alphavantage.co/query"

# 项目 interval → Alpha Vantage interval（仅分钟线）
_INTRADAY_INTERVAL_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "60min",
}

_SUPPORTED_INTERVALS = {*_INTRADAY_INTERVAL_MAP.keys(), "1d"}


class AlphaVantageDataSource(BaseDataSource):
    """Alpha Vantage 数据源，支持美股当日数据（15分钟延迟）"""

    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
        api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            raise ValueError(
                "需要设置环境变量 ALPHA_VANTAGE_API_KEY（免费注册: https://alphavantage.co）"
            )

        if interval not in _SUPPORTED_INTERVALS:
            raise ValueError(
                f"Alpha Vantage 不支持 interval={interval}，可用: {sorted(_SUPPORTED_INTERVALS)}"
            )

        av_symbol = symbol.strip().upper()

        logger.info(
            "alphavantage fetch | symbol=%s interval=%s period=%s~%s",
            av_symbol, interval, start, end,
        )

        if interval == "1d":
            df = self._fetch_daily(av_symbol, api_key)
        else:
            av_interval = _INTRADAY_INTERVAL_MAP[interval]
            df = self._fetch_intraday(av_symbol, av_interval, api_key)

        # 按日期范围过滤
        start_dt = pd.Timestamp(start)
        end_dt = pd.Timestamp(end) + pd.Timedelta(days=1)
        df = df[(df.index >= start_dt) & (df.index < end_dt)]

        if df.empty:
            raise ValueError(
                f"Alpha Vantage 在 {start}~{end} 范围内无数据: {av_symbol}"
            )

        return df

    def _fetch_daily(self, symbol: str, api_key: str) -> pd.DataFrame:
        resp = requests.get(
            _API_URL,
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "full",
                "apikey": api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        self._check_error(data)

        ts_key = "Time Series (Daily)"
        if ts_key not in data:
            raise ValueError(f"Alpha Vantage 未返回日线数据: {symbol}")

        return self._parse_time_series(data[ts_key])

    def _fetch_intraday(
        self, symbol: str, av_interval: str, api_key: str
    ) -> pd.DataFrame:
        resp = requests.get(
            _API_URL,
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": av_interval,
                "outputsize": "full",
                "apikey": api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        self._check_error(data)

        ts_key = f"Time Series ({av_interval})"
        if ts_key not in data:
            raise ValueError(
                f"Alpha Vantage 未返回分钟线数据: {symbol} ({av_interval})"
            )

        return self._parse_time_series(data[ts_key])

    @staticmethod
    def _check_error(data: dict) -> None:
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API 错误: {data['Error Message']}")
        if "Note" in data:
            raise ValueError(f"Alpha Vantage API 限流: {data['Note']}")
        if "Information" in data:
            raise ValueError(f"Alpha Vantage API 提示: {data['Information']}")

    @staticmethod
    def _parse_time_series(ts: dict) -> pd.DataFrame:
        """将 Alpha Vantage 的嵌套时间序列 JSON 解析为标准 DataFrame"""
        records = []
        for dt_str, values in ts.items():
            records.append({
                "datetime": dt_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            })

        df = pd.DataFrame(records)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime")
        df = df.sort_index()
        return df
