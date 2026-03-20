import { useState } from "react";
import { useI18n } from "../i18n";
import type { StrategyMeta } from "../strategies";

interface Props {
  meta: StrategyMeta;
  onSubmit: (
    strategyParams: Record<string, number>,
    common: { symbol: string; start_date: string; end_date: string; init_cash: number; fees: number }
  ) => void;
  loading: boolean;
}

export default function StrategyForm({ meta, onSubmit, loading }: Props) {
  const { t } = useI18n();
  const [symbol, setSymbol] = useState("AAPL");
  const [startDate, setStartDate] = useState("2025-01-01");
  const [endDate, setEndDate] = useState("2025-12-31");
  const [initCash, setInitCash] = useState(10000);
  const [fees, setFees] = useState(0.001);

  const [strategyParams, setStrategyParams] = useState<Record<string, number>>(() => {
    const defaults: Record<string, number> = {};
    for (const p of meta.params) {
      defaults[p.key] = p.default;
    }
    return defaults;
  });

  const handleParamChange = (key: string, value: number) => {
    setStrategyParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(strategyParams, {
      symbol,
      start_date: startDate,
      end_date: endDate,
      init_cash: initCash,
      fees,
    });
  };

  return (
    <form className="backtest-form" onSubmit={handleSubmit}>
      <div className="form-section-title">{t("form.basic_params")}</div>
      <div className="form-row">
        <label>
          {t("form.symbol")}
          <input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
        </label>
        <label>
          {t("form.start_date")}
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </label>
        <label>
          {t("form.end_date")}
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </label>
      </div>
      <div className="form-row">
        <label>
          {t("form.init_cash")}
          <input type="number" value={initCash} onChange={(e) => setInitCash(Number(e.target.value))} />
        </label>
        <label>
          {t("form.fees")}
          <input type="number" step="0.0001" value={fees} onChange={(e) => setFees(Number(e.target.value))} />
        </label>
      </div>

      <div className="form-section-title">{t("form.strategy_params")}</div>
      <div className="form-row">
        {meta.params.map((p) => (
          <label key={p.key}>
            {t(p.labelKey)}
            <input
              type="number"
              step={p.step ?? 1}
              value={strategyParams[p.key]}
              onChange={(e) => handleParamChange(p.key, Number(e.target.value))}
            />
          </label>
        ))}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? t("form.running") : t("form.run")}
      </button>
    </form>
  );
}
