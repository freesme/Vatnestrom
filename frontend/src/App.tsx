import { useState } from "react";
import BacktestForm from "./components/BacktestForm";
import Chart from "./components/Chart";
import StatsPanel from "./components/StatsPanel";
import { runBacktest } from "./api";
import type { BacktestRequest, BacktestResult } from "./types";
import "./App.css";

function App() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (params: BacktestRequest) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runBacktest(params);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "回测失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>VectorBT Playground</h1>

      <BacktestForm onSubmit={handleSubmit} loading={loading} />

      {error && <div className="error-msg">{error}</div>}

      {result && (
        <>
          <Chart ohlcv={result.ohlcv} signals={result.signals} indicators={result.indicators} symbol={result.symbol} />
          <StatsPanel stats={result.stats} />
        </>
      )}
    </div>
  );
}

export default App;
