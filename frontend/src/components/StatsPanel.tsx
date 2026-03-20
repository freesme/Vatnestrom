import { useI18n } from "../i18n";

interface Props {
  stats: Record<string, string | number | null>;
}

export default function StatsPanel({ stats }: Props) {
  const { t } = useI18n();

  return (
    <div className="rounded-xl border border-dark-border bg-dark-card p-5">
      <h3 className="mb-4 text-base font-semibold">{t("stats.title")}</h3>
      <div className="overflow-hidden rounded-lg">
        <table className="w-full text-sm">
          <tbody>
            {Object.entries(stats).map(([key, value], i) => (
              <tr
                key={key}
                className={i % 2 === 0 ? "bg-dark-input/50" : ""}
              >
                <td className="px-3 py-2 text-text-secondary">{t(`stats.${key}`, key)}</td>
                <td className="px-3 py-2 text-right font-mono text-text-primary">
                  {value ?? "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
