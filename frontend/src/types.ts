/** 单根 K 线数据，对应 lightweight-charts 的 CandlestickData */
export interface OhlcvItem {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/** 买卖信号点位 */
export interface Signal {
  date: string;
  action: "buy" | "sell";
  price: number;
}

/** 技术指标线的单个数据点 */
export interface IndicatorPoint {
  time: string;
  value: number;
}

/** 一条技术指标线（如 MA5、MA20） */
export interface Indicator {
  name: string;
  color: string;
  data: IndicatorPoint[];
  /** 是否叠加在主图上（默认 true）。false 表示独立面板（如 RSI、MACD） */
  overlay?: boolean;
}

/** 一笔交易记录（由后端 portfolio 配对生成） */
export interface Trade {
  id: number;
  buy_date: string;
  buy_price: number;
  sell_date: string | null;
  sell_price: number | null;
  pnl: number | null;
  pnl_pct: number | null;
  status: "win" | "loss" | "flat" | "open";
}

/** 回测请求参数 */
export interface BacktestRequest {
  symbol: string;
  start_date: string;
  end_date: string;
  init_cash: number;
  fees: number;
  strategy: string;
  strategy_params: Record<string, number>;
}

/** 回测 API 返回结果 */
export interface BacktestResult {
  symbol: string;
  strategy: string;
  params: Record<string, number>;
  ohlcv: OhlcvItem[];
  signals: Signal[];
  trades: Trade[];
  indicators: Indicator[];
  stats: Record<string, string | number | null>;
}

/** 批量回测请求参数 */
export interface BatchBacktestRequest {
  symbols: string[];
  start_date: string;
  end_date: string;
  init_cash: number;
  fees: number;
  strategy: string;
  strategy_params: Record<string, number>;
}

/** 批量回测中单个结果项（支持部分失败） */
export interface BatchResultItem {
  status: "success" | "error";
  data?: BacktestResult;
  symbol?: string;
  error?: string;
}

/** 批量回测 API 返回结果 */
export interface BatchBacktestResponse {
  results: BatchResultItem[];
}
