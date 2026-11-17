import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowSquareOut, CalendarPlus } from "@phosphor-icons/react";
import { api } from "../../api";
import { Loading, ErrorState, PageHeading } from "../../components/Shared";
import { countdown, icsFor, type Contest } from "./ics";

type Source = { platform: string; ok: boolean; fetchedAt: string | null };
const PLATFORMS = ["All", "Codeforces", "AtCoder"] as const;

function download(c: Contest) {
  const url = URL.createObjectURL(new Blob([icsFor(c)], { type: "text/calendar" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = `${c.id}.ics`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

const time = (iso: string) => new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
const day = (iso: string) => new Date(iso).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
const length = (m: number) => (m >= 1440 ? `${Math.round(m / 1440)} days` : m % 60 ? `${Math.floor(m / 60)} h ${m % 60} min` : `${m / 60} h`);

/** Upcoming contests from Codeforces and AtCoder, in the learner's own time zone. */
export default function Contests() {
  const [platform, setPlatform] = useState<(typeof PLATFORMS)[number]>("All");
  const [, tick] = useState(0);
  const contests = useQuery({
    queryKey: ["contests"],
    queryFn: () => api<{ contests: Contest[]; sources: Source[] }>("/contests"),
    staleTime: 10 * 60_000,
  });
  useEffect(() => {
    const t = setInterval(() => tick((n) => n + 1), 60_000);
    return () => clearInterval(t);
  }, []);

  if (contests.isLoading) return <Loading />;
  if (contests.error || !contests.data) return <ErrorState error={contests.error} retry={() => contests.refetch()} />;
  const shown = contests.data.contests.filter((c) => platform === "All" || c.platform === platform);
  const days = [...new Set(shown.map((c) => day(c.start)))];
  const down = contests.data.sources.filter((s) => !s.ok);

  return (
    <>
      <PageHeading
        title="Contests"
        description="Upcoming rated contests from Codeforces and AtCoder, shown in your time zone. Add any of them to your calendar."
      />
      {down.length > 0 && (
        <p className="inline-alert" role="status">
          {down.map((s) => s.platform).join(" and ")} couldn&apos;t be reached just now
          {down.some((s) => s.fetchedAt) ? ", so its list is from the last successful check" : ""}. The others are current.
        </p>
      )}
      <div className="contest-filters" role="group" aria-label="Platform">
        {PLATFORMS.map((p) => (
          <button key={p} type="button" className={platform === p ? "active" : ""} aria-pressed={platform === p} onClick={() => setPlatform(p)}>
            {p}
          </button>
        ))}
      </div>
      {!shown.length && <p className="muted">No upcoming contests listed here right now.</p>}
      {days.map((d) => (
        <section key={d} className="contest-group">
          <h2 className="contest-day">{d}</h2>
          <ul className="contest-list">
            {shown
              .filter((c) => day(c.start) === d)
              .map((c) => (
                <li key={c.id} className="contest-row">
                  <time dateTime={c.start}>{time(c.start)}</time>
                  <div className="contest-main">
                    <a href={c.url} target="_blank" rel="noreferrer">
                      {c.title}
                      <ArrowSquareOut size={14} aria-hidden="true" />
                    </a>
                    <span className="muted">
                      {c.platform}, {length(c.durationMinutes)}
                    </span>
                  </div>
                  <span className={"contest-when " + (countdown(c) === "live now" ? "live" : "")}>{countdown(c)}</span>
                  <button className="button small" type="button" onClick={() => download(c)} aria-label={`Add ${c.title} to calendar`}>
                    <CalendarPlus size={16} aria-hidden="true" /> Add to calendar
                  </button>
                </li>
              ))}
          </ul>
        </section>
      ))}
      <p className="muted contest-more">
        LeetCode and CodeChef do not publish a schedule we may read, so check them directly:{" "}
        <a href="https://leetcode.com/contest/" target="_blank" rel="noreferrer">
          LeetCode contests
        </a>{" "}
        and{" "}
        <a href="https://www.codechef.com/contests" target="_blank" rel="noreferrer">
          CodeChef contests
        </a>
        .
      </p>
    </>
  );
}
