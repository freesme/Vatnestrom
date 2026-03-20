# 图表功能说明文档

## 概述

本项目使用 [TradingView Lightweight Charts v5](https://github.com/nickliqian/lightweight-charts) 在浏览器中渲染交互式金融图表，将回测结果以 K 线图 + 技术指标线 + 买卖信号标记的形式直观展示给用户。

## 整体架构

```
用户操作表单 ──> 前端调用 API ──> 后端执行回测 ──> 返回图表数据 ──> 前端渲染图表
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                  OHLCV           Signals          Indicators
                 (K 线数据)       (买卖信号)        (技术指标线)
```

### 数据流

1. 用户在 `BacktestForm` 中填写参数，点击「执行回测」
2. 前端 `api.ts` 发起 `POST /backtest/run` 请求
3. 后端回测服务返回包含 `ohlcv`、`signals`、`indicators`、`stats` 的 JSON
4. 前端 `Chart` 组件接收数据，渲染完整图表

## 图表组成

图表由以下四层叠加构成，从底到顶依次为：

### 1. 成交量柱状图（底部）

- **位置**：图表底部 20% 区域
- **颜色**：收盘价 >= 开盘价时为半透明绿色，否则为半透明红色
- **用途**：辅助判断价量关系

### 2. K 线（主体）

- **类型**：标准蜡烛图（Candlestick）
- **配色**：
  - 上涨（收盘 > 开盘）：绿色 `#22c55e`
  - 下跌（收盘 < 开盘）：红色 `#ef4444`
- **数据字段**：`time`、`open`、`high`、`low`、`close`

### 3. 技术指标线（叠加层）

- **类型**：`LineSeries`，每条指标线独立一个系列
- **来源**：由各策略的 `generate_indicators()` 方法提供
- **渲染方式**：遍历后端返回的 `indicators` 数组，逐条创建线系列
- **以 ma_cross 策略为例**：
  - 快速均线（如 MA5）：橙色 `#f59e0b`
  - 慢速均线（如 MA20）：蓝色 `#3b82f6`

### 4. 买卖信号标记（最顶层）

- **类型**：`SeriesMarkers`（通过 `createSeriesMarkers` 创建）
- **买入信号**：K 线下方绿色上箭头，标注 `买 {价格}`
- **卖出信号**：K 线上方红色下箭头，标注 `卖 {价格}`

## API 数据格式

### 请求 `POST /backtest/run`

```json
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2025-12-31",
  "init_cash": 10000,
  "fees": 0.001,
  "strategy": "ma_cross",
  "strategy_params": { "fast_window": 5, "slow_window": 20 }
}
```

### 响应（图表相关字段）

```json
{
  "ohlcv": [
    { "time": "2024-01-02", "open": 185.5, "high": 186.1, "low": 184.0, "close": 185.8, "volume": 45200000 }
  ],
  "signals": [
    { "date": "2024-02-15", "action": "buy",  "price": 188.50 },
    { "date": "2024-03-20", "action": "sell", "price": 195.30 }
  ],
  "indicators": [
    {
      "name": "MA5",
      "color": "#f59e0b",
      "data": [
        { "time": "2024-01-08", "value": 186.20 }
      ]
    },
    {
      "name": "MA20",
      "color": "#3b82f6",
      "data": [
        { "time": "2024-01-30", "value": 185.90 }
      ]
    }
  ],
  "stats": { "..." : "..." }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `ohlcv` | `array` | K 线数据，每条包含 time/open/high/low/close/volume |
| `signals` | `array` | 买卖信号点位，包含 date/action/price |
| `indicators` | `array` | 技术指标线，每条包含 name/color/data |
| `indicators[].data` | `array` | 指标线的数据点，包含 time/value，已过滤 NaN |

## 前端组件说明

### `Chart.tsx`

图表渲染的核心组件，职责：

```
Props
├── ohlcv: OhlcvItem[]        K 线数据
├── signals: Signal[]         买卖信号
├── indicators: Indicator[]   技术指标线
└── symbol: string            股票代码（用于触发重绘）
```

**生命周期**：
- `useEffect` 监听 `[ohlcv, signals, indicators, symbol]` 变化
- 变化时销毁旧图表，创建新图表
- 组件卸载时清理事件监听和图表实例

**自适应**：监听 `window.resize` 事件，自动调整图表宽度。

### `BacktestForm.tsx`

回测参数表单，用户可配置：
- 股票代码、起止日期
- 初始资金、手续费
- 策略参数（快线周期、慢线周期）

### `StatsPanel.tsx`

回测统计指标展示表格，以键值对形式展示 `stats` 中的所有指标。

## 扩展指标线

图表的指标线渲染是**通用的**，前端不关心具体策略类型，只要后端返回 `indicators` 数组即可自动叠加显示。扩展步骤：

### 后端

在策略类中覆写 `generate_indicators()` 方法：

```python
# 示例：RSI 策略返回 RSI 曲线 + 超买超卖水平线
class RSIStrategy(BaseStrategy):

    def generate_indicators(self, price: pd.Series, params: dict) -> list[dict]:
        rsi = vbt.RSI.run(price, window=params.get("window", 14))
        return [
            {
                "name": "RSI",
                "color": "#a855f7",
                "data": _series_to_line_data(rsi.rsi),
            },
        ]
```

**要求**：
- 每条指标线必须包含 `name`（图例名称）、`color`（线条颜色）、`data`（数据点数组）
- `data` 中每个点为 `{"time": "YYYY-MM-DD", "value": float}`
- 需过滤 NaN 值（窗口期前几个数据点无值）

### 前端

**无需改动**。`Chart.tsx` 会自动遍历 `indicators` 数组，为每条指标线创建一个 `LineSeries`。

## 图表交互

Lightweight Charts 内置以下交互能力：

| 操作 | 效果 |
|------|------|
| 鼠标拖拽 | 平移时间轴 |
| 鼠标滚轮 | 缩放时间轴 |
| 鼠标悬停 | 十字准线跟随，显示对应时间和价格 |
| 双指缩放（触屏） | 缩放时间轴 |
| 窗口缩放 | 图表自动调整宽度 |

## 主题配置

当前使用深色主题，配色定义在 `Chart.tsx` 中：

```typescript
layout: {
  background: { color: "#1e1e2f" },  // 深蓝灰背景
  textColor: "#d1d5db",              // 浅灰文字
},
grid: {
  vertLines: { color: "#2d2d44" },   // 暗色网格线
  horzLines: { color: "#2d2d44" },
},
```

如需切换主题，修改以上颜色值即可。
