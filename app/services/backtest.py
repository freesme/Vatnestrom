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

import logging
import time

import numpy as np
import pandas as pd
import vectorbt as vbt

from app.core.config import BacktestConfig
from app.services.data import fetch_ohlcv
from app.strategies import get_strategy
from app.strategies.utils import format_time, is_intraday, set_intraday_context

logger = logging.getLogger(__name__)


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
    t_total = time.perf_counter()
    intraday = is_intraday(config.interval)
    logger.info("backtest start | symbol=%s strategy=%s interval=%s period=%s~%s",
                config.symbol, config.strategy, config.interval, config.start_date, config.end_date)

    # 第一步：获取完整的 OHLCV 历史数据
    t0 = time.perf_counter()
    ohlcv_df = fetch_ohlcv(config.symbol, config.start_date, config.end_date, config.interval, source=config.source)
    logger.info("fetch_ohlcv done | %.3fs | rows=%d", time.perf_counter() - t0, len(ohlcv_df))
    # 提取收盘价用于策略信号计算
    price = ohlcv_df["close"]

    # 第二步：根据策略名称获取策略实例，并生成买卖信号
    t0 = time.perf_counter()
    strategy = get_strategy(config.strategy)
    entries, exits = strategy.generate_signals(price, config.strategy_params, ohlcv=ohlcv_df)
    logger.info("generate_signals done | %.3fs", time.perf_counter() - t0)

    # 第三步：使用 vectorbt 构建投资组合，模拟交易过程
    t0 = time.perf_counter()
    portfolio = vbt.Portfolio.from_signals(
        close=price,          # 收盘价序列
        entries=entries,      # 买入信号
        exits=exits,          # 卖出信号
        init_cash=config.init_cash,  # 初始资金
        fees=config.fees,     # 手续费比例
        freq=config.freq,     # 数据频率
    )
    logger.info("portfolio.from_signals done | %.3fs", time.perf_counter() - t0)

    # 第四步：获取回测统计指标（收益率、夏普比率、最大回撤等）
    t0 = time.perf_counter()
    stats = portfolio.stats()
    logger.info("portfolio.stats done | %.3fs", time.perf_counter() - t0)

    # 第五步：从 portfolio 提取实际执行的买卖信号（而非原始策略信号）
    t0 = time.perf_counter()
    signals = _extract_portfolio_signals(portfolio, price, intraday)
    logger.info("extract_signals done | %.3fs | count=%d", time.perf_counter() - t0, len(signals))

    # 第六步：从 portfolio 提取完整交易记录（配对的买入卖出）
    t0 = time.perf_counter()
    trades = _extract_trades(portfolio, price, intraday)
    logger.info("extract_trades done | %.3fs | count=%d", time.perf_counter() - t0, len(trades))

    # 第七步：将 OHLCV 数据转换为前端 lightweight-charts 所需的格式
    t0 = time.perf_counter()
    ohlcv_list = _format_ohlcv(ohlcv_df, intraday)
    logger.info("format_ohlcv done | %.3fs", time.perf_counter() - t0)

    # 第八步：生成策略对应的技术指标线数据（如均线）
    t0 = time.perf_counter()
    set_intraday_context(intraday)
    indicators = strategy.generate_indicators(price, config.strategy_params, ohlcv=ohlcv_df)
    logger.info("generate_indicators done | %.3fs", time.perf_counter() - t0)

    # 将结果组装为字典，并清除所有非 JSON 安全的浮点值（NaN / Inf → None）
    t0 = time.perf_counter()
    result = {
        "symbol": config.symbol,
        "strategy": config.strategy,
        "params": config.strategy_params,
        "ohlcv": ohlcv_list,
        "signals": signals,
        "trades": trades,
        "indicators": indicators,
        "stats": {k: _serialize(v) for k, v in stats.items()},
    }
    result = _sanitize(result)
    logger.info("sanitize done | %.3fs", time.perf_counter() - t0)

    logger.info("backtest complete | total=%.3fs", time.perf_counter() - t_total)
    return result


def _format_ohlcv(df: pd.DataFrame, intraday: bool = False) -> list[dict]:
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
            "time": format_time(date, intraday),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": int(row["volume"]),
        })
    return records


def _extract_portfolio_signals(portfolio, price: pd.Series, intraday: bool = False) -> list[dict]:
    """从 portfolio 的 orders 中提取实际执行的买卖信号

    只返回 portfolio 真正执行的订单，而非策略产生的原始信号。
    这确保图表标记与实际交易记录完全一致。

    Returns:
        按日期排序的信号列表，例如:
        [
            {"date": "2025-11-10", "action": "buy",  "price": 150.25},
            {"date": "2025-12-05", "action": "sell", "price": 162.30},
        ]
    """
    signals = []
    orders = portfolio.orders.records_readable

    for _, order in orders.iterrows():
        date = pd.Timestamp(order["Timestamp"])
        signals.append({
            "date": format_time(date, intraday),
            "action": "buy" if order["Side"] == "Buy" else "sell",
            "price": round(float(order["Price"]), 2),
        })

    signals.sort(key=lambda x: x["date"])
    return signals


def _extract_trades(portfolio, price: pd.Series, intraday: bool = False) -> list[dict]:
    """从 portfolio 中提取配对的交易记录

    返回每笔交易的买入/卖出日期、价格、盈亏等详细信息。

    Returns:
        交易记录列表，例如:
        [
            {
                "id": 1,
                "buy_date": "2025-01-10", "buy_price": 150.25,
                "sell_date": "2025-02-05", "sell_price": 162.30,
                "pnl": 12.05, "pnl_pct": 8.02, "status": "win"
            },
        ]
    """
    trades_list = []
    trades = portfolio.trades.records_readable

    for i, (_, trade) in enumerate(trades.iterrows()):
        entry_date = format_time(pd.Timestamp(trade["Entry Timestamp"]), intraday)
        entry_price = round(float(trade["Avg Entry Price"]), 2)

        status_val = trade["Status"]
        is_open = str(status_val) == "Open"

        if is_open:
            trades_list.append({
                "id": i + 1,
                "buy_date": entry_date,
                "buy_price": entry_price,
                "sell_date": None,
                "sell_price": None,
                "pnl": None,
                "pnl_pct": None,
                "status": "open",
            })
        else:
            exit_date = format_time(pd.Timestamp(trade["Exit Timestamp"]), intraday)
            exit_price = round(float(trade["Avg Exit Price"]), 2)
            pnl = round(float(trade["PnL"]), 2)
            ret = float(trade["Return"])
            pnl_pct = round(ret * 100, 2)

            if pnl > 0:
                status = "win"
            elif pnl < 0:
                status = "loss"
            else:
                status = "flat"

            trades_list.append({
                "id": i + 1,
                "buy_date": entry_date,
                "buy_price": entry_price,
                "sell_date": exit_date,
                "sell_price": exit_price,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "status": status,
            })

    return trades_list


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


def _sanitize(obj):
    """递归将结果转换为纯 JSON 安全的 Python 原生类型

    处理所有 numpy/pandas 类型以及 NaN/Infinity。
    """
    if isinstance(obj, dict):
        return {str(k): _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    # numpy / Python 浮点 → 检查 NaN/Inf
    if isinstance(obj, (float, np.floating)):
        f = float(obj)
        if f != f or f == float("inf") or f == float("-inf"):  # NaN / Inf
            return None
        return f
    # numpy 整数
    if isinstance(obj, (np.integer,)):
        return int(obj)
    # numpy 布尔
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    # pandas 时间类型
    if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    # 原生安全类型直接返回
    if isinstance(obj, (str, int, bool, type(None))):
        return obj
    # 兜底：转字符串
    return str(obj)
