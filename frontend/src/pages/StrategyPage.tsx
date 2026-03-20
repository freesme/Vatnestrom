import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { STRATEGIES } from "../strategies";
import { useI18n } from "../i18n";
import Chart from "../components/Chart";
import StatsPanel from "../components/StatsPanel";
import TradesTable from "../components/TradesTable";
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
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <p className="mb-4 rounded-lg bg-red-900/40 px-4 py-3 text-red-300">
          {t("app.unknown_strategy")}: {id}
        </p>
        <button
          className="text-sm text-text-secondary transition-colors hover:text-text-primary"
          onClick={() => navigate("/")}
        >
          {t("app.back")}
        </button>
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
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <button
        className="mb-5 text-sm text-text-secondary transition-colors hover:text-text-primary"
        onClick={() => navigate("/")}
      >
        {t("app.back")}
      </button>

      {/* 策略头部 */}
      <div
        className="mb-6 flex items-center gap-4 rounded-xl border border-dark-border bg-dark-card p-5"
        style={{ borderLeftWidth: 4, borderLeftColor: meta.color }}
      >
        <span className="text-4xl">{meta.icon}</span>
        <div className="min-w-0">
          <h1 className="mb-1 text-xl font-bold">{t(meta.nameKey)}</h1>
          <p className="text-sm leading-relaxed text-text-secondary">{t(meta.descKey)}</p>
        </div>
      </div>

      <StrategyForm meta={meta} onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="mb-5 rounded-lg bg-red-900/40 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-5">
          <Chart ohlcv={result.ohlcv} signals={result.signals} indicators={result.indicators} symbol={result.symbol} />
          <TradesTable trades={result.trades} />
          <StatsPanel stats={result.stats} />
        </div>
      )}
    </div>
  );
}
