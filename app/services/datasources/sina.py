"""
新浪财经数据源适配器

通过新浪财经 K 线 API 获取 A 股历史行情数据，支持当日实时数据。
仅支持沪深 A 股（.SS / .SZ 后缀或 6 位纯数字代码）。
"""

import logging
import re

import pandas as pd
import requests

from app.services.datasources.base import BaseDataSource

logger = logging.getLogger(__name__)

# interval → 新浪 API 的 scale 参数
_INTERVAL_TO_SCALE = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
    "1h": 60,
    "1d": 240,
}

# 新浪 K 线 API 每次最多返回的数据条数
_MAX_DATALEN = 1023

_KLINE_URL = (
    "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
    "/CN_MarketData.getKLineData"
)


def _to_sina_symbol(symbol: str) -> str:
    """将通用股票代码转换为新浪格式

    600519.SS → sh600519
    000858.SZ → sz000858
    600519    → sh600519 (6开头自动判断沪市)
    000858    → sz000858 (其余自动判断深市)
    """
    symbol = symbol.strip().upper()

    # 带后缀格式
    if symbol.endswith(".SS"):
        return "sh" + symbol[:-3]
    if symbol.endswith(".SZ"):
        return "sz" + symbol[:-3]

    # 6位纯数字
    code = symbol.lstrip("0123456789") == ""
    if code and len(symbol) == 6:
        if symbol.startswith("6"):
            return "sh" + symbol
        return "sz" + symbol

    raise ValueError(
        f"新浪财经仅支持 A 股代码（如 600519.SS、000858.SZ），不支持: {symbol}"
    )


class SinaDataSource(BaseDataSource):
    """新浪财经数据源，支持 A 股当日实时数据"""

    def fetch_ohlcv(
        self, symbol: str, start: str, end: str, interval: str = "1d"
    ) -> pd.DataFrame:
        if interval not in _INTERVAL_TO_SCALE:
            supported = list(_INTERVAL_TO_SCALE.keys())
            raise ValueError(
                f"新浪财经不支持 interval={interval}，可用: {supported}"
            )

        sina_symbol = _to_sina_symbol(symbol)
        scale = _INTERVAL_TO_SCALE[interval]

        # 计算需要的数据条数（粗略估算，多取一些再按日期过滤）
        start_dt = pd.Timestamp(start)
        end_dt = pd.Timestamp(end)
        if interval == "1d":
            datalen = min((end_dt - start_dt).days + 50, _MAX_DATALEN)
        else:
            # 分钟线：每天约 4 小时 = 240 分钟交易时间
            bars_per_day = 240 // scale
            days = (end_dt - start_dt).days + 1
            datalen = min(bars_per_day * days + 50, _MAX_DATALEN)

        datalen = max(datalen, 100)

        logger.info(
            "sina fetch | symbol=%s scale=%d datalen=%d",
            sina_symbol, scale, datalen,
        )

        resp = requests.get(
            _KLINE_URL,
            params={
                "symbol": sina_symbol,
                "scale": scale,
                "ma": "no",
                "datalen": datalen,
            },
            timeout=15,
        )
        resp.raise_for_status()

        # 新浪返回的是非标准 JSON（键名无引号），需要特殊处理
        text = resp.text.strip()
        if not text or text == "null":
            raise ValueError(f"新浪财经未返回数据: {sina_symbol}")

        # 将 JS 对象格式转为标准 JSON（给键名加引号）
        text = re.sub(r'(\w+)\s*:', r'"\1":', text)
        records = pd.read_json(text, orient="records")

        if records.empty:
            raise ValueError(f"新浪财经返回空数据: {sina_symbol}")

        # 构造标准 DataFrame
        records["day"] = pd.to_datetime(records["day"])
        records = records.set_index("day")
        records = records.sort_index()

        df = pd.DataFrame({
            "open": pd.to_numeric(records["open"], errors="coerce"),
            "high": pd.to_numeric(records["high"], errors="coerce"),
            "low": pd.to_numeric(records["low"], errors="coerce"),
            "close": pd.to_numeric(records["close"], errors="coerce"),
            "volume": pd.to_numeric(records["volume"], errors="coerce"),
        })

        df = df.dropna()

        # 按日期范围过滤
        df = df[df.index >= start_dt]
        if interval == "1d":
            df = df[df.index <= end_dt + pd.Timedelta(days=1)]
        else:
            df = df[df.index <= end_dt + pd.Timedelta(days=1)]

        if df.empty:
            raise ValueError(
                f"新浪财经在 {start}~{end} 范围内无数据: {sina_symbol}"
            )

        return df
