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

# --- 股票池：覆盖美股各行业，尽量让每次请求的 symbol 不同以绕过缓存 ---
SYMBOLS = [
    # 科技
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSM", "AVGO", "ORCL",
    "ADBE", "CRM", "AMD", "INTC", "QCOM", "TXN", "AMAT", "MU", "LRCX", "SNPS",
    # 消费 / 零售
    "TSLA", "NKE", "SBUX", "MCD", "HD", "LOW", "TGT", "COST", "WMT", "PG",
    # 金融
    "JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SCHW", "AXP", "V",
    # 医疗
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "BMY", "AMGN",
    # 能源 / 工业
    "XOM", "CVX", "COP", "SLB", "EOG", "BA", "CAT", "GE", "HON", "UPS",
]

# --- 策略定义：每个策略带多组不同参数，制造更多不可缓存的组合 ---
STRATEGY_POOL = [
    # ma_cross — 不同快慢窗口
    {"strategy": "ma_cross", "strategy_params": {"fast_window": 5, "slow_window": 20}},
    {"strategy": "ma_cross", "strategy_params": {"fast_window": 10, "slow_window": 50}},
    {"strategy": "ma_cross", "strategy_params": {"fast_window": 20, "slow_window": 100}},
    {"strategy": "ma_cross", "strategy_params": {"fast_window": 8, "slow_window": 30}},
    # rsi — 不同窗口和阈值
    {"strategy": "rsi", "strategy_params": {"rsi_window": 7, "oversold": 25, "overbought": 75}},
    {"strategy": "rsi", "strategy_params": {"rsi_window": 14, "oversold": 30, "overbought": 70}},
    {"strategy": "rsi", "strategy_params": {"rsi_window": 21, "oversold": 35, "overbought": 65}},
    # bollinger — 不同窗口和标准差
    {"strategy": "bollinger", "strategy_params": {"bb_window": 15, "bb_std": 1.5}},
    {"strategy": "bollinger", "strategy_params": {"bb_window": 20, "bb_std": 2.0}},
    {"strategy": "bollinger", "strategy_params": {"bb_window": 30, "bb_std": 2.5}},
    # macd — 不同窗口组合
    {"strategy": "macd", "strategy_params": {"fast_window": 12, "slow_window": 26, "signal_window": 9}},
    {"strategy": "macd", "strategy_params": {"fast_window": 8, "slow_window": 21, "signal_window": 5}},
    {"strategy": "macd", "strategy_params": {"fast_window": 16, "slow_window": 36, "signal_window": 12}},
    # donchian — 不同入场/出场窗口
    {"strategy": "donchian", "strategy_params": {"entry_window": 20, "exit_window": 10}},
    {"strategy": "donchian", "strategy_params": {"entry_window": 55, "exit_window": 20}},
    {"strategy": "donchian", "strategy_params": {"entry_window": 10, "exit_window": 5}},
    # kdj — 不同窗口和阈值
    {"strategy": "kdj", "strategy_params": {"k_window": 9, "d_window": 3, "oversold": 20, "overbought": 80}},
    {"strategy": "kdj", "strategy_params": {"k_window": 14, "d_window": 5, "oversold": 25, "overbought": 75}},
    # mean_reversion — 不同窗口和阈值
    {"strategy": "mean_reversion", "strategy_params": {"ma_window": 10, "threshold": 3.0}},
    {"strategy": "mean_reversion", "strategy_params": {"ma_window": 20, "threshold": 5.0}},
    {"strategy": "mean_reversion", "strategy_params": {"ma_window": 40, "threshold": 8.0}},
    # atr_channel — 不同窗口和倍数
    {"strategy": "atr_channel", "strategy_params": {"atr_window": 10, "ma_window": 15, "multiplier": 1.5}},
    {"strategy": "atr_channel", "strategy_params": {"atr_window": 14, "ma_window": 20, "multiplier": 2.0}},
    {"strategy": "atr_channel", "strategy_params": {"atr_window": 20, "ma_window": 30, "multiplier": 3.0}},
]

# --- 日期范围池：不同的历史区间，进一步打散缓存 ---
DATE_RANGES = [
    ("2018-01-01", "2019-12-31"),
    ("2019-01-01", "2020-12-31"),
    ("2019-06-01", "2021-06-30"),
    ("2020-01-01", "2021-12-31"),
    ("2020-06-01", "2022-06-30"),
    ("2021-01-01", "2022-12-31"),
    ("2021-06-01", "2023-06-30"),
    ("2022-01-01", "2023-12-31"),
    ("2022-06-01", "2024-06-30"),
    ("2023-01-01", "2024-12-31"),
]

INIT_CASH_OPTIONS = [50_000, 100_000, 200_000, 500_000]
FEES_OPTIONS = [0.0005, 0.001, 0.002]


class BacktestUser(HttpUser):
    """模拟真实用户行为：偶尔访问首页，主要执行回测请求"""

    wait_time = between(1, 5)

    @task(1)
    def health_check(self):
        """轻量请求 — 测试基础吞吐量"""
        self.client.get("/")

    @task(3)
    def run_backtest(self):
        """核心接口 — POST /backtest/run

        每次请求随机组合 symbol x strategy x params x date_range，
        最大化组合数以绕过 yfinance / 框架层缓存。
        总组合数: 60 symbols x 24 strategies x 10 dates x 4 cash x 3 fees = 172,800
        """
        symbol = random.choice(SYMBOLS)
        strategy_cfg = random.choice(STRATEGY_POOL)
        start_date, end_date = random.choice(DATE_RANGES)

        payload = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "init_cash": random.choice(INIT_CASH_OPTIONS),
            "fees": random.choice(FEES_OPTIONS),
            "strategy": strategy_cfg["strategy"],
            "strategy_params": strategy_cfg["strategy_params"],
        }
        self.client.post("/backtest/run", json=payload)
