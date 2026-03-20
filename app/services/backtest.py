"""
回测执行服务模块

核心业务逻辑层，负责串联数据获取、信号生成、组合模拟三个步骤，
最终输出回测统计结果。

回测流程:
  1. 通过 data 模块获取历史价格数据
  2. 通过策略模块生成买卖信号
  3. 使用 vectorbt.Portfolio 模拟交易并计算绩效指标
  4. 将结果序列化为 JSON 兼容格式返回
"""

import numpy as np
import pandas as pd
import vectorbt as vbt

from app.core.config import BacktestConfig
from app.services.data import fetch_ohlcv
from app.strategies import get_strategy


def run_backtest(config: BacktestConfig) -> dict:
    """执行完整的回测流程

    Args:
        config: 回测配置对象，包含股票代码、日期范围、资金、策略等全部参数

    Returns:
        包含以下字段的字典:
        - symbol: 回测的股票代码
        - strategy: 使用的策略名称
        - params: 策略参数
        - ohlcv: K 线数据列表，供前端图表渲染
        - signals: 买卖信号及对应价格点位
        - stats: 回测统计指标（总收益率、夏普比率、最大回撤等）
    """
    # 第一步：获取完整的 OHLCV 历史数据
    ohlcv_df = fetch_ohlcv(config.symbol, config.start_date, config.end_date)
    # 提取收盘价用于策略信号计算
    price = ohlcv_df["close"]

    # 第二步：根据策略名称获取策略实例，并生成买卖信号
    strategy = get_strategy(config.strategy)
    entries, exits = strategy.generate_signals(price, config.strategy_params)

    # 第三步：使用 vectorbt 构建投资组合，模拟交易过程
    portfolio = vbt.Portfolio.from_signals(
        close=price,          # 收盘价序列
        entries=entries,      # 买入信号
        exits=exits,          # 卖出信号
        init_cash=config.init_cash,  # 初始资金
        fees=config.fees,     # 手续费比例
        freq=config.freq,     # 数据频率
    )

    # 第四步：获取回测统计指标（收益率、夏普比率、最大回撤等）
    stats = portfolio.stats()

    # 第五步：提取买卖信号对应的价格点位
    signals = _extract_signals(price, entries, exits)

    # 第六步：将 OHLCV 数据转换为前端 lightweight-charts 所需的格式
    ohlcv_list = _format_ohlcv(ohlcv_df)

    # 第七步：生成策略对应的技术指标线数据（如均线）
    indicators = strategy.generate_indicators(price, config.strategy_params)

    # 将结果组装为字典
    return {
        "symbol": config.symbol,
        "strategy": config.strategy,
        "params": config.strategy_params,
        "ohlcv": ohlcv_list,
        "signals": signals,
        "indicators": indicators,
        "stats": {k: _serialize(v) for k, v in stats.items()},
    }


def _format_ohlcv(df: pd.DataFrame) -> list[dict]:
    """将 OHLCV DataFrame 转换为 lightweight-charts 所需的数据格式

    lightweight-charts 要求每条 K 线数据为:
    { time: "YYYY-MM-DD", open: float, high: float, low: float, close: float, volume: float }

    Args:
        df: 包含 open/high/low/close/volume 列的 DataFrame

    Returns:
        K 线数据列表，按日期排序
    """
    records = []
    for date, row in df.iterrows():
        records.append({
            "time": str(date.date()),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": int(row["volume"]),
        })
    return records


def _extract_signals(price: pd.Series, entries: pd.Series, exits: pd.Series) -> list[dict]:
    """提取买卖信号对应的日期和价格点位

    将布尔信号序列转换为具体的交易记录列表，每条记录包含：
    日期、操作类型（buy/sell）、对应的收盘价。

    Args:
        price: 收盘价序列
        entries: 买入信号布尔序列
        exits: 卖出信号布尔序列

    Returns:
        按日期排序的信号列表，例如:
        [
            {"date": "2025-11-10", "action": "buy",  "price": 150.25},
            {"date": "2025-12-05", "action": "sell", "price": 162.30},
        ]
    """
    signals = []

    # 提取所有买入信号的日期和价格
    buy_dates = entries[entries].index
    for date in buy_dates:
        signals.append({
            "date": str(date.date()),
            "action": "buy",
            "price": round(float(price[date]), 2),
        })

    # 提取所有卖出信号的日期和价格
    sell_dates = exits[exits].index
    for date in sell_dates:
        signals.append({
            "date": str(date.date()),
            "action": "sell",
            "price": round(float(price[date]), 2),
        })

    # 按日期排序，方便查看交易时间线
    signals.sort(key=lambda x: x["date"])

    return signals


def _serialize(v):
    """将 numpy/pandas 特殊类型转换为 JSON 可序列化的 Python 原生类型

    vectorbt 返回的统计指标中包含 numpy 整数、浮点数、pandas Timedelta 等类型，
    这些类型无法直接被 JSON 序列化，需要逐一转换。
    特别注意：当数据不足以产生交易时，部分指标会返回 NaN 或 Infinity，
    这些值不符合 JSON 标准，需要转为 None。

    Args:
        v: 待转换的值

    Returns:
        转换后的 Python 原生类型值
    """
    # 优先处理 NaN 和 Infinity，它们不是合法的 JSON 值
    try:
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            return None
        if isinstance(v, (np.floating, np.integer)) and (np.isnan(v) or np.isinf(v)):
            return None
    except (TypeError, ValueError):
        pass

    # numpy 整数类型 -> Python int
    if isinstance(v, (np.integer,)):
        return int(v)
    # numpy 浮点类型 -> Python float，保留 6 位小数
    if isinstance(v, (np.floating,)):
        return round(float(v), 6)
    # pandas 时间差类型 -> 字符串表示（如 "365 days"）
    if isinstance(v, pd.Timedelta):
        return str(v)
    # Python 原生 float 也需检查（虽然前面已处理，这里做兜底）
    if isinstance(v, float):
        return round(v, 6)
    # 其他非原生类型统一转为字符串，原生类型直接返回
    return str(v) if not isinstance(v, (int, float, str, bool, type(None))) else v
