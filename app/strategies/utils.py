"""
策略公共工具函数
"""

import threading

import numpy as np
import pandas as pd

# 分钟/小时级别的 interval
_INTRADAY_INTERVALS = {"1m", "2m", "3m", "5m", "15m", "30m", "60m", "1h", "4h", "12h"}

# 线程局部存储：当前回测是否为日内数据
_ctx = threading.local()


def is_intraday(interval: str) -> bool:
    """判断是否为日内（分钟/小时）级别的 interval"""
    return interval in _INTRADAY_INTERVALS


def set_intraday_context(intraday: bool) -> None:
    """设置当前线程的日内数据上下文"""
    _ctx.intraday = intraday


def _get_intraday_context() -> bool:
    """获取当前线程的日内数据上下文"""
    return getattr(_ctx, "intraday", False)


def format_time(dt, intraday: bool = False) -> str | int:
    """将时间戳格式化为 lightweight-charts 兼容格式

    日线输出 "YYYY-MM-DD" 字符串；分钟/小时线输出 Unix 时间戳（秒）。
    """
    ts = pd.Timestamp(dt)
    if intraday:
        return int(ts.timestamp())
    return str(ts.date())


def series_to_line_data(series: pd.Series) -> list[dict]:
    """将 pandas Series 转换为 lightweight-charts LineSeries 所需的数据格式

    自动从线程上下文读取是否为日内数据，无需调用方传参。
    跳过 NaN 值（指标窗口期内前几个数据点没有值）。
    """
    intraday = _get_intraday_context()
    data = []
    for date, value in series.items():
        if np.isnan(value):
            continue
        data.append({
            "time": format_time(date, intraday),
            "value": round(float(value), 2),
        })
    return data
