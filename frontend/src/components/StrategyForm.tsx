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

const inputClass =
  "w-full rounded-lg border border-dark-border bg-dark-input px-3 py-2 text-sm text-text-primary outline-none transition-colors focus:border-accent";

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
    <form
      className="mb-6 space-y-5 rounded-xl border border-dark-border bg-dark-card p-5"
      onSubmit={handleSubmit}
    >
      {/* 基本参数 */}
      <fieldset>
        <legend className="mb-3 text-xs font-medium tracking-wider text-text-muted uppercase">
          {t("form.basic_params")}
        </legend>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          <label className="space-y-1 col-span-2 sm:col-span-1">
            <span className="text-xs text-text-secondary">{t("form.symbol")}</span>
            <input className={inputClass} value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="AAPL / 600519.SS" />
            <span className="text-[11px] leading-tight text-text-muted">{t("form.symbol_hint")}</span>
          </label>
          <label className="space-y-1">
            <span className="text-xs text-text-secondary">{t("form.start_date")}</span>
            <input className={inputClass} type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-text-secondary">{t("form.end_date")}</span>
            <input className={inputClass} type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-text-secondary">{t("form.init_cash")}</span>
            <input className={inputClass} type="number" value={initCash} onChange={(e) => setInitCash(Number(e.target.value))} />
          </label>
          <label className="space-y-1">
            <span className="text-xs text-text-secondary">{t("form.fees")}</span>
            <input className={inputClass} type="number" step="0.0001" value={fees} onChange={(e) => setFees(Number(e.target.value))} />
          </label>
        </div>
      </fieldset>

      {/* 策略参数 */}
      <fieldset>
        <legend className="mb-3 text-xs font-medium tracking-wider text-text-muted uppercase">
          {t("form.strategy_params")}
        </legend>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {meta.params.map((p) => (
            <label key={p.key} className="space-y-1">
              <span className="text-xs text-text-secondary">{t(p.labelKey)}</span>
              <input
                className={inputClass}
                type="number"
                step={p.step ?? 1}
                value={strategyParams[p.key]}
                onChange={(e) => handleParamChange(p.key, Number(e.target.value))}
              />
            </label>
          ))}
        </div>
      </fieldset>

      <button
        type="submit"
        disabled={loading}
        className="w-full cursor-pointer rounded-lg bg-accent py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:bg-gray-600"
      >
        {loading ? t("form.running") : t("form.run")}
      </button>
    </form>
  );
}
