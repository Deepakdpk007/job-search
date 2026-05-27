import { api, type Job } from "@/lib/api";

export const dynamic = "force-dynamic";

type SearchParams = {
  city?: string;
  skill?: string;
  experience?: string;
  employment_type?: string;
};

export default async function JobsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  let jobs: Job[] = [];
  let error: string | null = null;
  try {
    jobs = await api.jobs({ ...params, limit: 50 });
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load jobs";
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Jobs</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          {jobs.length} active postings. Use URL params: <code>?city=Bengaluru</code>,
          <code>?skill=kafka</code>, <code>?experience=fresher</code>.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      <ul className="space-y-3">
        {jobs.map((j) => (
          <li
            key={j.id}
            className="rounded-md border border-zinc-200 p-4 dark:border-zinc-800"
          >
            <div className="flex items-baseline justify-between gap-4">
              <div>
                <a
                  href={j.apply_url ?? "#"}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold hover:underline"
                >
                  {j.title}
                </a>
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  {j.company.name}
                  {j.city ? ` · ${j.city}` : ""}
                  {j.experience_band ? ` · ${j.experience_band}` : ""}
                </div>
              </div>
              {j.posted_at && (
                <time className="shrink-0 text-xs text-zinc-500">
                  {new Date(j.posted_at).toLocaleDateString()}
                </time>
              )}
            </div>
            {j.skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {j.skills.map((s) => (
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
