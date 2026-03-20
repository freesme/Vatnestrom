"""双均线交叉策略单元测试

使用构造的价格数据验证 MACrossStrategy 的信号生成逻辑，
不依赖网络请求，不会超时。
"""

import pandas as pd
import pytest

from app.strategies.ma_cross import MACrossStrategy


@pytest.fixture
def strategy():
    return MACrossStrategy()


@pytest.fixture
def params():
    """使用较小的窗口期，方便构造测试数据"""
    return {"fast_window": 2, "slow_window": 4}


def _make_price(values: list[float]) -> pd.Series:
    """用给定数值列表构造价格序列"""
    dates = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=dates, name="Close")


class TestMACrossSignals:
    """测试 generate_signals 方法"""

    def test_returns_two_bool_series(self, strategy, params):
        """返回值应为两个布尔型 Series（entries 和 exits）"""
        price = _make_price([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        entries, exits = strategy.generate_signals(price, params)

        assert isinstance(entries, pd.Series)
        assert isinstance(exits, pd.Series)
        assert entries.dtype == bool
        assert exits.dtype == bool
        assert len(entries) == len(price)
        assert len(exits) == len(price)

    def test_golden_cross(self, strategy, params):
        """价格先跌后涨，快线上穿慢线时应产生买入信号（金叉）"""
        # 先下降让快线 < 慢线，再上升让快线 > 慢线
        price = _make_price([10, 9, 8, 7, 6, 5, 6, 8, 10, 12])
        entries, exits = strategy.generate_signals(price, params)

        # 上升阶段应至少出现一次买入信号
        assert entries.any(), "应当产生至少一个金叉买入信号"

    def test_death_cross(self, strategy, params):
        """价格先涨后跌，快线下穿慢线时应产生卖出信号（死叉）"""
        # 先上升让快线 > 慢线，再下降让快线 < 慢线
        price = _make_price([5, 6, 8, 10, 12, 11, 9, 7, 5, 3])
        entries, exits = strategy.generate_signals(price, params)

        # 下降阶段应至少出现一次卖出信号
        assert exits.any(), "应当产生至少一个死叉卖出信号"

    def test_no_signal_on_flat_price(self, strategy, params):
        """价格恒定时，均线完全重合，不应产生任何交叉信号"""
        price = _make_price([10.0] * 20)
        entries, exits = strategy.generate_signals(price, params)

        assert not entries.any(), "价格恒定时不应有买入信号"
        assert not exits.any(), "价格恒定时不应有卖出信号"

    def test_entries_exits_not_simultaneous(self, strategy, params):
        """同一时刻不应同时出现买入和卖出信号"""
        price = _make_price([10, 9, 8, 7, 6, 5, 6, 8, 10, 12, 11, 9, 7, 5, 3])
        entries, exits = strategy.generate_signals(price, params)

        # 逐行检查：不应存在 entries=True 且 exits=True 的时刻
        simultaneous = entries & exits
        assert not simultaneous.any(), "同一时刻不应同时产生买入和卖出信号"

    def test_custom_params(self, strategy):
        """验证自定义窗口参数能正常工作"""
        price = _make_price(list(range(1, 51)))  # 50 个递增数据点
        params = {"fast_window": 5, "slow_window": 20}
        entries, exits = strategy.generate_signals(price, params)

        assert len(entries) == 50
        assert len(exits) == 50

    def test_default_params(self, strategy):
        """不传参数时应使用默认值（fast_window=10, slow_window=50）"""
        price = _make_price(list(range(1, 101)))  # 100 个数据点
        entries, exits = strategy.generate_signals(price, {})

        assert len(entries) == 100
