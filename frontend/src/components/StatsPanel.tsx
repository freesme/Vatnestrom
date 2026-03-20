import { useI18n } from "../i18n";

interface Props {
  stats: Record<string, string | number | null>;
}

export default function StatsPanel({ stats }: Props) {
  const { t } = useI18n();

  return (
    <div className="stats-panel">
      <h3>{t("stats.title")}</h3>
      <table>
        <tbody>
          {Object.entries(stats).map(([key, value]) => (
            <tr key={key}>
              <td className="stats-key">{t(`stats.${key}`, key)}</td>
              <td className="stats-value">{value ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
