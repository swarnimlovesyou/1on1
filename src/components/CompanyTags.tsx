import { Link } from "react-router-dom";

type Companies = Record<string, number> | { name: string; count: number }[] | undefined;

/** "Asked at" with the most-reported companies first, each linking to that company's questions. */
export default function CompanyTags({ companies, limit = 3 }: { companies: Companies; limit?: number }) {
  const rows = (Array.isArray(companies) ? companies.map((c) => [c.name, c.count] as const) : Object.entries(companies ?? {}))
    .filter(([, count]) => typeof count === "number" && count > 0)
    .sort((a, b) => b[1] - a[1]);
  if (!rows.length) return null;
  const more = rows.length - limit;
  return (
    <span className="asked-at" title="Community-reported LeetCode company tags, data as of May 2022">
      <span className="asked-at-label">Asked at</span>
      {rows.slice(0, limit).map(([name, count]) => (
        <Link key={name} to={`/practice?tab=bank&company=${encodeURIComponent(name)}`} aria-label={name} title={`${name}: reported ${count} times`}>
          {name}
        </Link>
      ))}
      {more > 0 && <span className="asked-at-more">+{more} more</span>}
    </span>
  );
}
