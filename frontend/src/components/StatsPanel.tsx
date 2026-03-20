interface Props {
  stats: Record<string, string | number | null>;
}

/** 回测统计指标展示面板 */
export default function StatsPanel({ stats }: Props) {
  return (
    <div className="stats-panel">
      <h3>回测统计</h3>
      <table>
        <tbody>
          {Object.entries(stats).map(([key, value]) => (
            <tr key={key}>
              <td className="stats-key">{key}</td>
              <td className="stats-value">{value ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
