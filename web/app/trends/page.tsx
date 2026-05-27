import { api, type SkillTrend } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TrendsPage() {
  let trends: SkillTrend[] = [];
  let error: string | null = null;
  try {
    trends = await api.skillTrends(30, 20);
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load trends";
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Skill Trends</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Last 30 days. Growth = last 7 days vs prior 7 days.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {!error && trends.length === 0 && (
        <p className="text-sm text-zinc-500">
          No trend data yet. Run ingestion with <code>--rollup</code> to populate
          the trend table.
        </p>
      )}

      <table className="w-full text-sm">
        <thead className="border-b border-zinc-200 text-left dark:border-zinc-800">
          <tr>
            <th className="py-2">Skill</th>
            <th className="py-2 text-right">Total jobs (30d)</th>
            <th className="py-2 text-right">7d growth</th>
          </tr>
        </thead>
        <tbody>
          {trends.map((t) => (
            <tr
              key={t.skill}
              className="border-b border-zinc-100 dark:border-zinc-900"
            >
              <td className="py-2">{t.skill}</td>
              <td className="py-2 text-right tabular-nums">{t.total}</td>
              <td
                className={`py-2 text-right tabular-nums ${
                  t.growth_pct_30d == null
                    ? "text-zinc-400"
                    : t.growth_pct_30d >= 0
                    ? "text-emerald-600"
                    : "text-rose-600"
                }`}
              >
                {t.growth_pct_30d == null
                  ? "—"
                  : `${t.growth_pct_30d > 0 ? "+" : ""}${t.growth_pct_30d}%`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
