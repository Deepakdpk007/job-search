import { api, type CityHeat } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HeatmapPage() {
  let cities: CityHeat[] = [];
  let error: string | null = null;
  try {
    cities = await api.cityHeatmap();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load heatmap";
  }

  const max = Math.max(1, ...cities.map((c) => c.job_count));

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">City Heatmap</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Active job count per city. Map visualization coming next; this is the
          tabular precursor.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          {error} — is the API running on localhost:8000?
        </div>
      )}

      {!error && cities.length === 0 && (
        <p className="text-sm text-zinc-500">
          No data yet. Run the ingestion: <code>python -m app.ingestion.run --source greenhouse --rollup</code>
        </p>
      )}

      <ul className="space-y-2">
        {cities.map((c) => (
          <li
            key={c.city}
            className="rounded-md border border-zinc-200 p-4 dark:border-zinc-800"
          >
            <div className="flex items-baseline justify-between">
              <h2 className="font-semibold">{c.city}</h2>
              <span className="text-sm tabular-nums text-zinc-500">
                {c.job_count} jobs
              </span>
            </div>
            <div className="mt-2 h-2 w-full overflow-hidden rounded bg-zinc-100 dark:bg-zinc-900">
              <div
                className="h-full bg-emerald-500"
                style={{ width: `${(c.job_count / max) * 100}%` }}
              />
            </div>
            {c.top_skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {c.top_skills.map((s) => (
                  <span
                    key={s}
                    className="rounded bg-zinc-100 px-2 py-0.5 text-xs dark:bg-zinc-800"
                  >
                    {s}
                  </span>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
