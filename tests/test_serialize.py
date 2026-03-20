"""_serialize 函数单元测试，确保所有类型都能正确转换为 JSON 兼容值"""

import json

import numpy as np
import pandas as pd

from app.services.backtest import _serialize


class TestSerialize:

    def test_nan_returns_none(self):
        """NaN 应转为 None（JSON null）"""
        assert _serialize(float("nan")) is None
        assert _serialize(np.float64("nan")) is None

    def test_inf_returns_none(self):
        """Infinity 应转为 None"""
        assert _serialize(float("inf")) is None
        assert _serialize(float("-inf")) is None
        assert _serialize(np.float64("inf")) is None

    def test_numpy_int(self):
        assert _serialize(np.int64(42)) == 42
        assert isinstance(_serialize(np.int64(42)), int)

    def test_numpy_float(self):
        result = _serialize(np.float64(3.14159265))
        assert isinstance(result, float)
        assert result == round(3.14159265, 6)

    def test_timedelta(self):
        td = pd.Timedelta(days=365)
        assert isinstance(_serialize(td), str)

    def test_python_native_types_passthrough(self):
        assert _serialize(123) == 123
        assert _serialize("hello") == "hello"
        assert _serialize(True) is True
        assert _serialize(None) is None

    def test_full_result_json_serializable(self):
        """模拟一组包含 NaN 的回测结果，确保整体可被 JSON 序列化"""
        mock_stats = {
            "Total Return": np.float64(0.15),
            "Sharpe Ratio": np.float64("nan"),
            "Max Drawdown": np.float64(-0.05),
            "Total Trades": np.int64(3),
            "Duration": pd.Timedelta(days=100),
            "Win Rate": float("nan"),
        }
        serialized = {k: _serialize(v) for k, v in mock_stats.items()}
        # 不应抛出异常
        result = json.dumps(serialized)
        assert '"null"' not in result  # None 应序列化为 null 而非 "null"
