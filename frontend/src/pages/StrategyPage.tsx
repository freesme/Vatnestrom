import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { STRATEGIES } from "../strategies";
import { useI18n } from "../i18n";
import Chart from "../components/Chart";
import StatsPanel from "../components/StatsPanel";
import StrategyForm from "../components/StrategyForm";
import { runBacktest } from "../api";
import type { BacktestResult } from "../types";

export default function StrategyPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useI18n();
  const meta = STRATEGIES.find((s) => s.id === id);

  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!meta) {
    return (
      <div className="app">
        <p className="error-msg">{t("app.unknown_strategy")}: {id}</p>
        <button className="btn-back" onClick={() => navigate("/")}>{t("app.back")}</button>
      </div>
    );
  }

  const handleSubmit = async (params: Record<string, number>, common: { symbol: string; start_date: string; end_date: string; init_cash: number; fees: number }) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runBacktest({
        ...common,
        strategy: meta.id,
        strategy_params: params,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("app.backtest_failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <button className="btn-back" onClick={() => navigate("/")}>{t("app.back")}</button>

      <div className="strategy-page-header" style={{ borderLeftColor: meta.color }}>
        <span className="strategy-icon-lg">{meta.icon}</span>
        <div>
          <h1>{t(meta.nameKey)}</h1>
          <p className="strategy-page-desc">{t(meta.descKey)}</p>
        </div>
      </div>

      <StrategyForm meta={meta} onSubmit={handleSubmit} loading={loading} />

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
