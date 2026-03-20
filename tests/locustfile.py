"""
Locust 压力测试脚本 — VectorBT Playground

使用方法:
  1. 启动后端:  uv run uvicorn main:app
  2. 启动 Locust: uv run locust -f tests/locustfile.py --host=http://127.0.0.1:8000
  3. 打开浏览器访问 http://localhost:8089
  4. 设置并发用户数和 spawn rate，点击 Start 开始压测

建议测试流程:
  - 先用 10 用户 / spawn rate 2 验证基本功能
  - 逐步增加到 50 -> 100 -> 200，观察响应时间和失败率拐点
"""

import random

from locust import HttpUser, between, task


# 预定义的回测参数组合（使用固定历史日期范围，避免当日数据 NaN 问题）
BACKTEST_SCENARIOS = [
    {
        "symbol": "AAPL",
        "strategy": "ma_cross",
        "strategy_params": {"fast_window": 10, "slow_window": 50},
    },
    {
        "symbol": "GOOGL",
        "strategy": "rsi",
        "strategy_params": {"rsi_window": 14, "oversold": 30, "overbought": 70},
    },
    {
        "symbol": "MSFT",
        "strategy": "bollinger",
        "strategy_params": {"bb_window": 20, "bb_std": 2.0},
    },
    {
        "symbol": "TSLA",
        "strategy": "macd",
        "strategy_params": {"fast_window": 12, "slow_window": 26, "signal_window": 9},
    },
    {
        "symbol": "AMZN",
        "strategy": "donchian",
        "strategy_params": {"window": 20},
    },
    {
        "symbol": "META",
        "strategy": "kdj",
        "strategy_params": {"k_window": 14, "d_window": 3},
    },
    {
        "symbol": "NVDA",
        "strategy": "mean_reversion",
        "strategy_params": {"window": 20, "std_dev": 2.0},
    },
    {
        "symbol": "AAPL",
        "strategy": "atr_channel",
        "strategy_params": {"atr_window": 14, "atr_multiplier": 2.0},
    },
]


class BacktestUser(HttpUser):
    """模拟真实用户行为：偶尔访问首页，主要执行回测请求"""

    wait_time = between(1, 5)

    @task(1)
    def health_check(self):
        """轻量请求 — 测试基础吞吐量"""
        self.client.get("/")

    @task(3)
    def run_backtest(self):
        """核心接口 — POST /backtest/run"""
        scenario = random.choice(BACKTEST_SCENARIOS)
        payload = {
            "symbol": scenario["symbol"],
            "start_date": "2022-01-01",
            "end_date": "2023-12-31",
            "init_cash": 100000,
            "fees": 0.001,
            "strategy": scenario["strategy"],
            "strategy_params": scenario["strategy_params"],
        }
        self.client.post("/backtest/run", json=payload)
