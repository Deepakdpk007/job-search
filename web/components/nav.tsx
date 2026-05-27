import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/heatmap", label: "Heatmap" },
  { href: "/trends", label: "Trends" },
  { href: "/jobs", label: "Jobs" },
];

export default function Nav() {
  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          job-search
        </Link>
        <nav className="flex gap-6 text-sm">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:underline">
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
