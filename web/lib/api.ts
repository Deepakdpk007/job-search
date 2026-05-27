const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Company = {
  id: number;
  slug: string;
  name: string;
  ats_source: string;
};

export type Job = {
  id: number;
  title: string;
  company: Company;
  city: string | null;
  country: string | null;
  employment_type: string | null;
  experience_band: string | null;
  apply_url: string | null;
  posted_at: string | null;
  skills: string[];
};

export type CityHeat = {
  city: string;
  job_count: number;
  top_skills: string[];
  top_roles: string[];
};

export type SkillTrend = {
  skill: string;
  total: number;
  growth_pct_30d: number | null;
  points: { bucket_date: string; job_count: number }[];
};

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  jobs: (params?: Record<string, string | number | undefined>) => {
    const qs = new URLSearchParams(
      Object.entries(params ?? {})
        .filter(([, v]) => v !== undefined && v !== "")
        .map(([k, v]) => [k, String(v)])
    ).toString();
    return fetchJson<Job[]>(`/api/jobs${qs ? `?${qs}` : ""}`);
  },
  cityHeatmap: () => fetchJson<CityHeat[]>("/api/heatmap/cities"),
  skillTrends: (days = 30, top = 20) =>
    fetchJson<SkillTrend[]>(`/api/trends/skills?days=${days}&top=${top}`),
};
