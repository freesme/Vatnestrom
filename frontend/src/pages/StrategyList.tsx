import { useNavigate } from "react-router-dom";
import { STRATEGIES } from "../strategies";
import { useI18n } from "../i18n";

export default function StrategyList() {
  const navigate = useNavigate();
  const { t } = useI18n();

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
      <div className="mb-10 text-center">
        <h1 className="mb-2 text-3xl font-bold tracking-tight">{t("app.title")}</h1>
        <p className="text-text-secondary">{t("app.subtitle")}</p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {STRATEGIES.map((s) => (
          <div
            key={s.id}
            className="group cursor-pointer rounded-xl border border-dark-border bg-dark-card p-6 transition-all duration-200 hover:-translate-y-1 hover:border-transparent hover:shadow-lg hover:shadow-black/30"
            style={{ borderLeftWidth: 3, borderLeftColor: s.color }}
            onClick={() => navigate(`/strategy/${s.id}`)}
          >
            <div className="mb-3 flex items-center gap-3">
              <span className="text-2xl">{s.icon}</span>
              <h2 className="text-base font-semibold">{t(s.nameKey)}</h2>
            </div>

            <p className="mb-4 text-sm leading-relaxed text-text-secondary">
              {t(s.descKey)}
            </p>

            <div className="mb-4 flex flex-wrap gap-1.5">
              {s.params.map((p) => (
                <span
                  key={p.key}
                  className="rounded-full bg-dark-input px-2.5 py-0.5 text-xs text-text-muted"
                >
                  {t(p.labelKey)}: {p.default}
                </span>
              ))}
            </div>

            <div
              className="text-right text-sm font-semibold opacity-70 transition-opacity group-hover:opacity-100"
              style={{ color: s.color }}
            >
              {t("app.start_backtest")}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
