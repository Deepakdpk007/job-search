import { api, type CityHeat } from "@/lib/api";
import IndiaHeatmap from "@/components/india-heatmap";

export const dynamic = "force-dynamic";

export default async function HeatmapPage() {
  let cities: CityHeat[] = [];
  let error: string | null = null;
  try {
    cities = await api.cityHeatmap();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load heatmap";
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">City Heatmap</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Active jobs per Indian metro. Bubble size scales with job count;
          hover for top skills.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          {error} — is the API running on localhost:8000?
        </div>
      )}

      {!error && cities.length === 0 && (
        <p className="text-sm text-zinc-500">
          No data yet. Run:{" "}
          <code>python -m app.ingestion.run --source greenhouse --rollup</code>
        </p>
      )}

      <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
        <IndiaHeatmap cities={cities} />
      </div>

      {cities.length > 0 && (
        <details className="rounded-md border border-zinc-200 dark:border-zinc-800">
          <summary className="cursor-pointer p-3 text-sm font-medium">
            Show as table
          </summary>
          <ul className="space-y-2 p-3 pt-0">
            {cities.map((c) => (
              <li
                key={c.city}
                className="flex items-baseline justify-between border-t border-zinc-100 py-2 dark:border-zinc-900"
              >
                <span className="font-medium">{c.city}</span>
                <span className="text-sm tabular-nums text-zinc-500">
                  {c.job_count}
                </span>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
