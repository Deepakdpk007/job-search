import Link from "next/link";

const cards = [
  {
    href: "/heatmap" as const,
    title: "City Heatmap",
    desc: "Where India is hiring right now — top cities, top skills, top roles.",
  },
  {
    href: "/trends" as const,
    title: "Skill Trends",
    desc: "Which skills are heating up. Kafka, Rust, GenAI, week over week.",
  },
  {
    href: "/jobs" as const,
    title: "Job Search",
    desc: "Filter by city, skill, experience, and employment type.",
  },
];

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="space-y-4">
        <h1 className="text-3xl font-bold tracking-tight">
          Hiring intelligence for India
        </h1>
        <p className="max-w-2xl text-zinc-600 dark:text-zinc-400">
          Daily-fresh job postings turned into heatmaps, skill trends, and role
          analytics. Built on Greenhouse, Lever, and Ashby data.
        </p>
      </section>
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((c) => (
          <Link
            key={c.href}
            href={c.href}
            className="rounded-lg border border-zinc-200 p-5 transition hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
          >
            <h2 className="font-semibold">{c.title}</h2>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              {c.desc}
            </p>
          </Link>
        ))}
      </section>
    </div>
  );
}
