import type { BacktestRequest, BacktestResult } from "./types";

const API_BASE = "http://localhost:8000";

/** 调用后端回测接口 */
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
