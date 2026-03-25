"""
TickFlow 数据源适配器

通过 TickFlow Python SDK 获取 A 股、美股、港股历史和实时行情数据。
免费版支持日线历史数据（无需 API Key）；付费版支持分钟线和实时数据。

股票代码格式：
  A 股: 600519.SH (沪) / 000858.SZ (深)
  美股: AAPL.US
  港股: 0700.HK

文档: https://docs.tickflow.org/zh-Hans
"""

import logging
import os

import pandas as pd
from tickflow import TickFlow

from app.services.datasources.base import BaseDataSource

logger = logging.getLogger(__name__)

# 项目 interval → TickFlow period
_PERIOD_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "60m",
    "1d": "1d",
}


def _to_tickflow_symbol(symbol: str) -> str:
    """将通用股票代码转换为 TickFlow 格式

    600519.SS → 600519.SH  (Yahoo 沪市后缀 .SS → TickFlow .SH)
    000858.SZ → 000858.SZ  (不变)
    AAPL      → AAPL.US    (无后缀美股自动加 .US)
    600519.SH → 600519.SH  (已是 TickFlow 格式)
    AAPL.US   → AAPL.US    (已是 TickFlow 格式)
    """
    symbol = symbol.strip()

    # Yahoo Finance 沪市后缀 .SS → TickFlow .SH
    if symbol.upper().endswith(".SS"):
        return symbol[:-3] + ".SH"

    # 已有市场后缀（.SH / .SZ / .US / .HK 等）
    if "." in symbol:
        return symbol.upper()

    # 6 位纯数字 → A 股
    if symbol.isdigit() and len(symbol) == 6:
        suffix = "SH" if symbol.startswith("6") else "SZ"
        return f"{symbol}.{suffix}"

    # 纯字母 → 美股
    if symbol.isalpha():
        return f"{symbol.upper()}.US"

    return symbol.upper()


def _create_client() -> TickFlow:
    """创建 TickFlow 客户端实例"""
    api_key = os.environ.get("TICKFLOW_API_KEY")
    if api_key:
        return TickFlow(api_key=api_key)
    # 无 API Key 时使用免费版（仅支持日线历史数据）
    return TickFlow.free()


class TickFlowDataSource(BaseDataSource):
    """TickFlow 数据源，支持 A 股、美股、港股"""

    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
        period = _PERIOD_MAP.get(interval)
        if not period:
            supported = list(_PERIOD_MAP.keys())
            raise ValueError(
                f"TickFlow 不支持 interval={interval}，可用: {supported}"
            )

        tf_symbol = _to_tickflow_symbol(symbol)

        # 日期转毫秒时间戳
        start_ms = int(pd.Timestamp(start).timestamp() * 1000)
        end_ms = int(pd.Timestamp(end).timestamp() * 1000)

        logger.info(
            "tickflow fetch | symbol=%s period=%s range=%s~%s",
            tf_symbol, period, start, end,
        )

        client = _create_client()
        raw_df = client.klines.get(
            symbol=tf_symbol,
            period=period,
            start_time=start_ms,
            end_time=end_ms,
            as_dataframe=True,
        )

        if raw_df is None or raw_df.empty:
            raise ValueError(f"TickFlow 在 {start}~{end} 范围内无数据: {tf_symbol}")

        # 构造标准 DatetimeIndex
        is_intraday = interval != "1d"
        if is_intraday and "trade_time" in raw_df.columns:
            # 分钟线：trade_time 包含完整时间信息
            raw_df.index = pd.to_datetime(raw_df["trade_time"])
        elif "trade_date" in raw_df.columns:
            # 日线：使用 trade_date
            raw_df.index = pd.to_datetime(raw_df["trade_date"])
        elif "timestamp" in raw_df.columns:
            raw_df.index = pd.to_datetime(raw_df["timestamp"], unit="ms")

        df = pd.DataFrame({
            "open": pd.to_numeric(raw_df["open"], errors="coerce"),
            "high": pd.to_numeric(raw_df["high"], errors="coerce"),
            "low": pd.to_numeric(raw_df["low"], errors="coerce"),
            "close": pd.to_numeric(raw_df["close"], errors="coerce"),
            "volume": pd.to_numeric(raw_df["volume"], errors="coerce"),
        })

        df = df.dropna()
        df = df.sort_index()

        if df.empty:
            raise ValueError(f"TickFlow 在 {start}~{end} 范围内无数据: {tf_symbol}")

        return df
