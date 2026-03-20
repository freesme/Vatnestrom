import { useNavigate } from "react-router-dom";
import { STRATEGIES } from "../strategies";
import { useI18n } from "../i18n";

export default function StrategyList() {
  const navigate = useNavigate();
  const { t } = useI18n();

  return (
    <div className="app">
      <h1>{t("app.title")}</h1>
      <p className="page-subtitle">{t("app.subtitle")}</p>

      <div className="strategy-grid">
        {STRATEGIES.map((s) => (
          <div
            key={s.id}
            className="strategy-card"
            style={{ borderColor: s.color }}
            onClick={() => navigate(`/strategy/${s.id}`)}
          >
            <div className="strategy-card-header">
              <span className="strategy-icon">{s.icon}</span>
              <h2 className="strategy-name">{t(s.nameKey)}</h2>
            </div>
            <p className="strategy-desc">{t(s.descKey)}</p>
            <div className="strategy-params-preview">
              {s.params.map((p) => (
                <span key={p.key} className="param-tag">
                  {t(p.labelKey)}: {p.default}
                </span>
              ))}
            </div>
            <div className="strategy-card-footer" style={{ color: s.color }}>
              {t("app.start_backtest")}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
