import type { BacktestRequest, BacktestResult, BatchBacktestRequest, BatchBacktestResponse } from "./types";

const API_BASE = import.meta.env.DEV ? "http://localhost:8000" : "";

/** 调用后端回测接口（单只股票） */
export async function runBacktest(params: BacktestRequest): Promise<BacktestResult> {
  const res = await fetch(`${API_BASE}/backtest/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    throw new Error(`回测请求失败: ${res.status}`);
  }
  return res.json();
}

/** 调用后端批量回测接口（多只股票并行） */
export async function runBatchBacktest(params: BatchBacktestRequest): Promise<BatchBacktestResponse> {
  const res = await fetch(`${API_BASE}/backtest/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    throw new Error(`批量回测请求失败: ${res.status}`);
  }
  return res.json();
}
