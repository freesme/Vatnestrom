import { useState } from "react";
import { useI18n } from "../i18n";
import type { Trade } from "../types";

interface Props {
  trades: Trade[];
}

const PAGE_SIZE = 15;

export default function TradesTable({ trades }: Props) {
  const { t } = useI18n();
  const [page, setPage] = useState(0);

  const totalPages = Math.max(1, Math.ceil(trades.length / PAGE_SIZE));
  const pageTrades = trades.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  if (trades.length === 0) return null;

  return (
    <div className="rounded-xl border border-dark-border bg-dark-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold">{t("trades.title")}</h3>
        <span className="text-xs text-text-muted">
          {t("trades.total")}: {trades.length}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-dark-border text-left text-xs text-text-muted">
              <th className="px-3 py-2 font-medium">#</th>
              <th className="px-3 py-2 font-medium">{t("trades.buy_date")}</th>
              <th className="px-3 py-2 font-medium text-right">{t("trades.buy_price")}</th>
              <th className="px-3 py-2 font-medium">{t("trades.sell_date")}</th>
              <th className="px-3 py-2 font-medium text-right">{t("trades.sell_price")}</th>
              <th className="px-3 py-2 font-medium text-right">{t("trades.pnl")}</th>
              <th className="px-3 py-2 font-medium text-right">{t("trades.pnl_pct")}</th>
              <th className="px-3 py-2 font-medium text-center">{t("trades.status")}</th>
            </tr>
          </thead>
          <tbody>
            {pageTrades.map((trade, i) => {
              const isWin = trade.status === "win";
              const isLoss = trade.status === "loss";
              const isOpen = trade.status === "open";
              const colorClass = isWin ? "text-green-400" : isLoss ? "text-red-400" : "";
              return (
                <tr
                  key={trade.id}
                  className={i % 2 === 0 ? "bg-dark-input/50" : ""}
                >
                  <td className="px-3 py-2 font-mono text-text-muted">{trade.id}</td>
                  <td className="px-3 py-2 font-mono">{trade.buy_date}</td>
                  <td className="px-3 py-2 text-right font-mono">{trade.buy_price}</td>
                  <td className="px-3 py-2 font-mono">{trade.sell_date ?? "-"}</td>
                  <td className="px-3 py-2 text-right font-mono">{trade.sell_price ?? "-"}</td>
                  <td className={`px-3 py-2 text-right font-mono ${colorClass}`}>
                    {trade.pnl !== null ? (trade.pnl > 0 ? `+${trade.pnl}` : trade.pnl) : "-"}
                  </td>
                  <td className={`px-3 py-2 text-right font-mono ${colorClass}`}>
                    {trade.pnl_pct !== null ? `${trade.pnl_pct > 0 ? "+" : ""}${trade.pnl_pct}%` : "-"}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {isOpen ? (
                      <span className="inline-block rounded-full bg-yellow-900/40 px-2 py-0.5 text-xs text-yellow-300">
                        {t("trades.open")}
                      </span>
                    ) : isWin ? (
                      <span className="inline-block rounded-full bg-green-900/40 px-2 py-0.5 text-xs text-green-300">
                        {t("trades.win")}
                      </span>
                    ) : isLoss ? (
                      <span className="inline-block rounded-full bg-red-900/40 px-2 py-0.5 text-xs text-red-300">
                        {t("trades.loss")}
                      </span>
                    ) : (
                      <span className="inline-block rounded-full bg-gray-700/40 px-2 py-0.5 text-xs text-text-muted">
                        {t("trades.flat")}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <button
            className="rounded border border-dark-border px-2.5 py-1 text-xs text-text-secondary transition-colors hover:bg-dark-card-hover disabled:opacity-40"
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
          >
            ‹
          </button>
          <span className="text-xs text-text-muted">
            {page + 1} / {totalPages}
          </span>
          <button
            className="rounded border border-dark-border px-2.5 py-1 text-xs text-text-secondary transition-colors hover:bg-dark-card-hover disabled:opacity-40"
            disabled={page >= totalPages - 1}
            onClick={() => setPage((p) => p + 1)}
          >
            ›
          </button>
        </div>
      )}
    </div>
  );
}
