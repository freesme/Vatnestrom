"""
Tushare 数据源适配器

通过 Tushare Pro API 获取 A 股历史行情数据。
需要在 .env 中配置 TUSHARE_TOKEN。

股票代码格式：
  A 股: 600519.SH (沪) / 000858.SZ (深)
  指数: 000001.SH (上证指数)

5000 积分可使用：日线、周线、月线、分钟线（1/5/15/30/60min）等接口。
文档: https://tushare.pro/document/2
"""

import logging
import os

import pandas as pd
import tushare as ts

from app.services.datasources.base import BaseDataSource

logger = logging.getLogger(__name__)

# 项目 interval → Tushare 分钟线 freq 参数
_MINUTE_FREQ_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "60min",
}


def _to_tushare_code(symbol: str) -> str:
    """将通用股票代码转换为 Tushare 格式

    600519      → 600519.SH
    000858      → 000858.SZ
    600519.SS   → 600519.SH  (Yahoo 沪市后缀)
    600519.SH   → 600519.SH  (已是 Tushare 格式)
    AAPL        → 不支持（Tushare 仅 A 股）
    """
    symbol = symbol.strip().upper()

    # Yahoo Finance 沪市后缀 .SS → Tushare .SH
    if symbol.endswith(".SS"):
        return symbol[:-3] + ".SH"

    # 已有后缀
    if "." in symbol:
        return symbol

    # 6 位纯数字 → A 股
    if symbol.isdigit() and len(symbol) == 6:
        suffix = "SH" if symbol.startswith(("6", "9")) else "SZ"
        return f"{symbol}.{suffix}"

    raise ValueError(
        f"Tushare 仅支持 A 股代码，不支持: {symbol}。"
        f"请使用 6 位数字代码（如 600519）或带后缀格式（如 600519.SH）"
    )


def _get_api() -> ts.pro_api:
    """创建 Tushare Pro API 实例"""
    token = os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        raise ValueError(
            "未配置 TUSHARE_TOKEN，请在 .env 文件中添加: TUSHARE_TOKEN=your_token"
        )
    return ts.pro_api(token)


class TushareDataSource(BaseDataSource):
    """Tushare Pro 数据源，仅支持 A 股"""

    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
        ts_code = _to_tushare_code(symbol)
        start_dt = start.replace("-", "")
        end_dt = end.replace("-", "")

        api = _get_api()

        if interval in _MINUTE_FREQ_MAP:
            df = self._fetch_minute(api, ts_code, start_dt, end_dt, interval)
        elif interval == "1d":
            df = self._fetch_daily(api, ts_code, start_dt, end_dt)
        else:
            raise ValueError(
                f"Tushare 不支持 interval={interval}，"
                f"可用: {list(_MINUTE_FREQ_MAP.keys()) + ['1d']}"
            )

        if df.empty:
            raise ValueError(f"Tushare 在 {start}~{end} 范围内无数据: {ts_code}")

        return df

    def _fetch_daily(
        self, api: ts.pro_api, ts_code: str, start: str, end: str
    ) -> pd.DataFrame:
        """获取日线数据"""
        logger.info("tushare daily | code=%s range=%s~%s", ts_code, start, end)

        df = api.daily(ts_code=ts_code, start_date=start, end_date=end)

        if df is None or df.empty:
            return pd.DataFrame()

        df.index = pd.to_datetime(df["trade_date"])
        df = df.sort_index()

        return pd.DataFrame({
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["vol"], errors="coerce"),
        }).dropna()

    def _fetch_minute(
        self, api: ts.pro_api, ts_code: str, start: str, end: str, interval: str
    ) -> pd.DataFrame:
        """获取分钟线数据"""
        freq = _MINUTE_FREQ_MAP[interval]
        logger.info(
            "tushare stk_mins | code=%s freq=%s range=%s~%s",
            ts_code, freq, start, end,
        )

        df = ts.pro_bar(
            ts_code=ts_code,
            freq=freq,
            start_date=start,
            end_date=end,
            asset="E",
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df.index = pd.to_datetime(df["trade_time"])
        df = df.sort_index()

        return pd.DataFrame({
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["vol"], errors="coerce"),
        }).dropna()
