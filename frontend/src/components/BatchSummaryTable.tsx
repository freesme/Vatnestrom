import { useI18n } from "../i18n";
import type { BacktestResult } from "../types";

interface Props {
  results: BacktestResult[];
  selectedSymbol: string | null;
  onSelect: (symbol: string) => void;
}

const STAT_KEYS = [
  { key: "Total Return [%]", i18nKey: "batch.total_return", colorize: true },
  { key: "Sharpe Ratio", i18nKey: "batch.sharpe", colorize: true },
  { key: "Max Drawdown [%]", i18nKey: "batch.max_drawdown", colorize: false },
  { key: "Win Rate [%]", i18nKey: "batch.win_rate", colorize: false },
  { key: "Total Trades", i18nKey: "batch.total_trades", colorize: false },
];

function formatVal(v: string | number | null | undefined): string {
  if (v == null) return "-";
  if (typeof v === "number") return Number.isFinite(v) ? String(Math.round(v * 100) / 100) : "-";
  return v;
}

function valColor(v: string | number | null | undefined, colorize: boolean): string {
  if (!colorize || v == null || typeof v !== "number") return "";
  return v > 0 ? "text-green-400" : v < 0 ? "text-red-400" : "";
}

export default function BatchSummaryTable({ results, selectedSymbol, onSelect }: Props) {
  const { t } = useI18n();

  const sorted = [...results].sort((a, b) => {
    const ra = a.stats["Total Return [%]"];
    const rb = b.stats["Total Return [%]"];
    return (typeof rb === "number" ? rb : -Infinity) - (typeof ra === "number" ? ra : -Infinity);
  });

  return (
    <div className="rounded-xl border border-dark-border bg-dark-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold">{t("batch.summary_title")}</h3>
        <span className="text-xs text-text-muted">{t("batch.click_hint")}</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-dark-border text-left text-xs text-text-muted">
              <th className="px-3 py-2 font-medium">{t("batch.symbol")}</th>
              {STAT_KEYS.map((s) => (
                <th key={s.key} className="px-3 py-2 font-medium text-right">
                  {t(s.i18nKey)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((result, i) => {
              const isSelected = result.symbol === selectedSymbol;
              return (
                <tr
                  key={result.symbol}
                  className={`cursor-pointer transition-colors hover:bg-dark-card-hover ${
                    isSelected
                      ? "bg-accent/10 border-l-2 border-l-accent"
                      : i % 2 === 0
                        ? "bg-dark-input/50"
                        : ""
                  }`}
                  onClick={() => onSelect(result.symbol)}
                >
                  <td className="px-3 py-2 font-semibold">{result.symbol}</td>
                  {STAT_KEYS.map((s) => {
                    const val = result.stats[s.key];
                    return (
                      <td
                        key={s.key}
                        className={`px-3 py-2 text-right font-mono ${valColor(val, s.colorize)}`}
                      >
                        {formatVal(val)}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
