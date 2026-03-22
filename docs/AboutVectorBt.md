# vectorbt 
vectorbt 是一个基于 Python 的量化交易回测与分析库，核心特点是向量化运算，速度极快。主要功能包括：

  数据获取

  - 内置数据下载器，支持从 Yahoo Finance、Binance 等获取历史行情数据
  - 支持自定义数据源

  回测引擎

  - 向量化回测 — 利用 NumPy/Numba 实现极高性能，比传统事件驱动回测快几个数量级
  - 支持对大量参数组合进行批量回测（参数网格搜索）
  - 支持多资产组合回测

  技术指标

  - 内置常见技术指标（MA、RSI、MACD、Bollinger Bands 等）
  - 可自定义指标，支持用 Numba JIT 加速
  - 指标工厂模式，方便批量生成和组合指标

  投资组合分析

  - 订单/交易/持仓的详细记录与分析
  - 收益率、夏普比率、最大回撤、Sortino 等绩效指标
  - 支持做多/做空、手续费、滑点设置

  可视化

  - 基于 Plotly 的交互式图表
  - K线图、指标叠加、权益曲线、回撤图等
  - 支持自定义图表布局

  信号生成

  - 基于指标交叉、阈值等生成入场/出场信号
  - 支持自定义信号逻辑

  其他

  - 支持 Numba JIT 编译自定义函数
  - 灵活的数据对齐和广播机制（类似 pandas）
  - 可与 pandas、NumPy 无缝集成


  uv sync
  uv run uvicorn main:app --reload

  # 终端 2：前端
  cd frontend/
  npm install
  npm run dev

  启动后访问：

  - 前端：http://localhost:5173
  - 后端接口文档：http://127.0.0.1:8000/docs
  - 后端健康检查：http://127.0.0.1:8000/