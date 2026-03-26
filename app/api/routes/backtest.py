"""
回测 API 路由模块

提供 HTTP 接口供前端或其他客户端调用回测服务。
所有回测相关的接口都挂载在 /backtest 前缀下。

接口列表:
  - POST /backtest/run  执行一次回测，返回统计结果
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import BacktestConfig, interval_to_freq
from app.services.backtest import run_backtest

logger = logging.getLogger(__name__)

# 创建路由器，统一前缀为 /backtest，在 Swagger 文档中归类到 "backtest" 标签
router = APIRouter(prefix="/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    """回测请求参数模型

    使用 Pydantic BaseModel 进行请求体校验和文档生成。
    所有字段都有默认值，可以只传入需要修改的参数。

    Attributes:
        symbol: 股票代码，如 "AAPL"、"GOOGL"、"TSLA"
        start_date: 回测起始日期
        end_date: 回测结束日期
        init_cash: 初始资金（美元）
        fees: 手续费比例（0.001 = 0.1%）
        strategy: 策略名称，需在策略注册表中存在
        strategy_params: 策略专属参数，键值对形式
    """
    symbol: str = "AAPL"
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    init_cash: float = 100_000.0
    fees: float = 0.001
    interval: str = "1d"
    source: str = "yahoo"
    strategy: str = "ma_cross"
    strategy_params: dict = {"fast_window": 10, "slow_window": 50}
    enable_tp_sl: bool = False


class BatchBacktestRequest(BaseModel):
    """批量回测请求参数模型

    支持同时对多只股票执行回测，其余参数与单只股票回测相同。

    Attributes:
        symbols: 股票代码列表，如 ["AAPL", "GOOGL", "TSLA"]，最多 20 只
    """
    symbols: list[str]
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    init_cash: float = 100_000.0
    fees: float = 0.001
    interval: str = "1d"
    source: str = "yahoo"
    strategy: str = "ma_cross"
    strategy_params: dict = {"fast_window": 10, "slow_window": 50}
    enable_tp_sl: bool = False


_executor = ThreadPoolExecutor(max_workers=8)


@router.post("/run")
def backtest_run(req: BacktestRequest):
    """执行回测接口

    接收回测参数，将 Pydantic 请求模型转换为内部配置对象，
    调用回测服务执行回测，返回统计结果。
    """
    logger.info("POST /backtest/run | symbol=%s strategy=%s", req.symbol, req.strategy)
    t0 = time.perf_counter()
    config = BacktestConfig(
        symbol=req.symbol,
        start_date=req.start_date,
        end_date=req.end_date,
        init_cash=req.init_cash,
        fees=req.fees,
        interval=req.interval,
        source=req.source,
        freq=interval_to_freq(req.interval),
        strategy=req.strategy,
        strategy_params=req.strategy_params,
        enable_tp_sl=req.enable_tp_sl,
    )
    result = run_backtest(config)
    logger.info("POST /backtest/run complete | %.3fs", time.perf_counter() - t0)
    return result


@router.post("/batch")
async def backtest_batch(req: BatchBacktestRequest):
    """批量回测接口

    接收多只股票代码，并行执行回测，返回每只股票的结果。
    支持部分失败：某只股票回测失败不影响其他股票。
    """
    # 校验
    symbols = list(dict.fromkeys(req.symbols))  # 去重并保持顺序
    if not symbols:
        raise HTTPException(status_code=400, detail="symbols 列表不能为空")
    if len(symbols) > 20:
        raise HTTPException(status_code=400, detail="单次最多回测 20 只股票")

    logger.info("POST /backtest/batch | symbols=%s strategy=%s", symbols, req.strategy)
    t0 = time.perf_counter()

    loop = asyncio.get_event_loop()

    async def run_one(symbol: str) -> dict:
        config = BacktestConfig(
            symbol=symbol,
            start_date=req.start_date,
            end_date=req.end_date,
            init_cash=req.init_cash,
            fees=req.fees,
            interval=req.interval,
            source=req.source,
            freq=interval_to_freq(req.interval),
            strategy=req.strategy,
            strategy_params=req.strategy_params,
            enable_tp_sl=req.enable_tp_sl,
        )
        try:
            result = await loop.run_in_executor(_executor, run_backtest, config)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.exception("Backtest failed for symbol=%s", symbol)
            return {"status": "error", "symbol": symbol, "error": str(e)}

    tasks = [run_one(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)

    logger.info("POST /backtest/batch complete | %.3fs | %d symbols", time.perf_counter() - t0, len(symbols))
    return {"results": list(results)}
