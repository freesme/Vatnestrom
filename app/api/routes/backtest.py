"""
回测 API 路由模块

提供 HTTP 接口供前端或其他客户端调用回测服务。
所有回测相关的接口都挂载在 /backtest 前缀下。

接口列表:
  - POST /backtest/run  执行一次回测，返回统计结果
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import BacktestConfig
from app.services.backtest import run_backtest

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
    strategy: str = "ma_cross"
    strategy_params: dict = {"fast_window": 10, "slow_window": 50}


@router.post("/run")
def backtest_run(req: BacktestRequest):
    """执行回测接口

    接收回测参数，将 Pydantic 请求模型转换为内部配置对象，
    调用回测服务执行回测，返回统计结果。

    请求示例:
        POST /backtest/run
        {
            "symbol": "AAPL",
            "strategy": "ma_cross",
            "strategy_params": {"fast_window": 10, "slow_window": 50}
        }
    """
    # 将 API 请求模型转换为内部配置数据类
    config = BacktestConfig(
        symbol=req.symbol,
        start_date=req.start_date,
        end_date=req.end_date,
        init_cash=req.init_cash,
        fees=req.fees,
        strategy=req.strategy,
        strategy_params=req.strategy_params,
    )
    # 调用回测服务并返回结果
    return run_backtest(config)
