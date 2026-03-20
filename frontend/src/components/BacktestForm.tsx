import { useState } from "react";
import type { BacktestRequest } from "../types";

interface Props {
  onSubmit: (params: BacktestRequest) => void;
  loading: boolean;
}

/** 回测参数表单组件 */
export default function BacktestForm({ onSubmit, loading }: Props) {
  const [symbol, setSymbol] = useState("AAPL");
  const [startDate, setStartDate] = useState("2025-01-01");
  const [endDate, setEndDate] = useState("2025-12-31");
  const [initCash, setInitCash] = useState(10000);
  const [fees, setFees] = useState(0.001);
  const [fastWindow, setFastWindow] = useState(5);
  const [slowWindow, setSlowWindow] = useState(20);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      symbol,
      start_date: startDate,
      end_date: endDate,
      init_cash: initCash,
      fees,
      strategy: "ma_cross",
      strategy_params: { fast_window: fastWindow, slow_window: slowWindow },
    });
  };

  return (
    <form className="backtest-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>
          股票代码
          <input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
        </label>
        <label>
          起始日期
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </label>
        <label>
          结束日期
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </label>
      </div>

      <div className="form-row">
        <label>
          初始资金
          <input type="number" value={initCash} onChange={(e) => setInitCash(Number(e.target.value))} />
        </label>
        <label>
          手续费
          <input type="number" step="0.0001" value={fees} onChange={(e) => setFees(Number(e.target.value))} />
        </label>
        <label>
          快线周期
          <input type="number" value={fastWindow} onChange={(e) => setFastWindow(Number(e.target.value))} />
        </label>
        <label>
          慢线周期
          <input type="number" value={slowWindow} onChange={(e) => setSlowWindow(Number(e.target.value))} />
        </label>
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "回测中..." : "执行回测"}
      </button>
    </form>
  );
}
