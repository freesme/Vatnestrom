"""
策略公共工具函数
"""

import numpy as np
import pandas as pd


def series_to_line_data(series: pd.Series) -> list[dict]:
    """将 pandas Series 转换为 lightweight-charts LineSeries 所需的数据格式

    跳过 NaN 值（指标窗口期内前几个数据点没有值）。

    Args:
        series: 指标值的时间序列

    Returns:
        [{"time": "2024-01-02", "value": 150.25}, ...] 格式的列表
    """
    data = []
    for date, value in series.items():
        if np.isnan(value):
            continue
        data.append({
            "time": str(date.date()),
            "value": round(float(value), 2),
        })
    return data
