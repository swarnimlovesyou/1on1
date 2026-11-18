import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Books, CalendarCheck, Code, Exam, Fire, ListChecks, Notebook, Trophy } from "@phosphor-icons/react";
import { api } from "../../api";
import { useApp } from "../../context";
import { useLearningMap } from "../LearningMap";
import { useLessons } from "../Learning";
import { countdown, type Contest } from "../contests/ics";
import { streak, weekCount, weeks } from "./activity";

type Report = { questionId: string; title: string; source: string; company: string; stage: string; month: string; reports: number };

const LINKS = [
  ["/learn", "Explore concepts", "L", Books],
  ["/practice", "Practice", "P", Code],
  ["/practice?tab=sheets", "Sheets", "S", ListChecks],
  ["/contests", "Contests", "C", Trophy],
  ["/prep", "Prep", "R", Exam],
  ["/notebook", "My notebook", "N", Notebook],
] as const;

function greeting(name?: string) {
  const h = new Date().getHours();
  const part = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  return name ? `${part}, ${name.split(" ")[0]}` : "Welcome to 1on1";
}

const monthName = (m: string) => new Date(m + "-01T00:00:00Z").toLocaleDateString(undefined, { month: "short", year: "numeric", timeZone: "UTC" });

/** Home: what to do next, how active you are, what is happening, and what learners were asked recently. */
export default function Dashboard() {
  const { user, progress } = useApp();
  const map = useLearningMap();
  const lessons = useLessons();
  const contests = useQuery({ queryKey: ["contests"], queryFn: () => api<{ contests: Contest[] }>("/contests"), retry: false, staleTime: 600_000 });
  const reports = useQuery({ queryKey: ["reports-recent"], queryFn: () => api<Report[]>("/reports/recent"), retry: false, staleTime: 60_000 });

  const activity = (progress.activity ?? {}) as Record<string, number>;
  const days = streak(activity);
  const week = weekCount(activity);
  const grid = weeks(activity);
  const next = map.data?.nextAction;
  const due = map.data?.reviewsDue ?? [];
  const upcoming = (contests.data?.contests ?? []).filter((c) => countdown(c) !== "ended").slice(0, 4);
  const total = lessons.data?.length ?? 33;

  return (
    <div className="dash">
      <header className="dash-head">
        <div>
          <h1>{greeting(user?.name)}</h1>
          <p className="muted">
            {new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" })}
            {user ? "" : ". Sign in to keep your streak and evidence."}
          </p>
        </div>
        {next && (
          <Link className="button primary" to={next.href}>
            Continue <ArrowRight size={16} aria-hidden="true" />
          </Link>
        )}
      </header>

      <section className="dash-next" aria-label="Your next step">
        <div className="dash-next-main">
          <span className="dash-label">Your next step</span>
          <strong>{next?.title ?? "Start with Time and Space Complexity"}</strong>
          <p>{next?.reason ?? "The first concept in prerequisite order."}</p>
          <Link className="button primary small" to={next?.href ?? "/learn/lesson-complexity"}>
            Open it
          </Link>
        </div>
        <ul className="dash-next-more">
          <li>
            <CalendarCheck size={18} aria-hidden="true" />
            <span>
              <strong>{due.length ? `${due.length} review${due.length === 1 ? "" : "s"} due` : "No reviews due"}</strong>
              <small>{due.length ? "Short checks before they fade." : "Reviews return when you are about to forget."}</small>
            </span>
            {due.length > 0 && <Link to={due[0].lessonId ? "/learn/" + due[0].lessonId + "#checkpoint" : "/learn"}>Review</Link>}
          </li>
          <li>
            <ListChecks size={18} aria-hidden="true" />
            <span>
              <strong>Your practice plan</strong>
              <small>Today's tasks, built around your goal date.</small>
            </span>
            <Link to="/plan">Open</Link>
          </li>
        </ul>
      </section>

      <section className="dash-stats" aria-label="Your numbers">
        <div className="dash-card dash-activity">
          <span className="dash-label">
            <Fire size={15} aria-hidden="true" /> Current streak
          </span>
          <strong>{days}</strong>
          <small>{days === 1 ? "day" : "days"} in a row</small>
        </div>
        <div className="dash-card">
          <span className="dash-label">This week</span>
          <strong>{week}</strong>
          <small>learning moments in the last 7 days</small>
        </div>
        <div className="dash-card">
          <span className="dash-label">Lessons explored</span>
          <strong>
            {progress.completed.length}
            <span className="dash-of"> of {total}</span>
          </strong>
          <small>across six families</small>
        </div>
        <div className="dash-card">
          <span className="dash-label">Problems solved</span>
          <strong>{progress.solved.length}</strong>
          <small>accepted by the judge</small>
        </div>
      </section>

      <div className="dash-columns">
        <section className="dash-card dash-heat-card" aria-labelledby="dash-heat-title">
          <div className="dash-card-head">
            <h2 id="dash-heat-title">Activity</h2>
            <Link to="/progress">Progress</Link>
          </div>
          <div className="dash-heat" role="img" aria-label={`Activity over 12 weeks: ${week} this week, streak ${days}`}>
            {grid.map((w, i) => (
              <div key={i}>
                {w.map((d) => (
                  <i key={d.date} data-date={d.date} data-level={d.count === 0 ? 0 : d.count < 3 ? 1 : d.count < 6 ? 2 : 3} title={`${d.date}: ${d.count}`} />
                ))}
              </div>
            ))}
          </div>
          <p className="muted dash-heat-key">
            12 weeks. Each square is a day; darker means more lessons, checks and solves.
          </p>
        </section>

        <section className="dash-card dash-happening" aria-labelledby="dash-happening-title">
          <div className="dash-card-head">
            <h2 id="dash-happening-title">What's happening</h2>
            <Link to="/contests">Contests</Link>
          </div>
          {upcoming.length ? (
            <ul>
              {upcoming.map((c) => (
                <li key={c.id}>
                  <span className="dash-when">{countdown(c)}</span>
                  <span>
                    <a href={c.url} target="_blank" rel="noreferrer">
                      {c.title}
                    </a>
                    <small>{c.platform}</small>
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">{contests.isLoading ? "Checking contest sites…" : "No contests listed right now."}</p>
          )}
        </section>
      </div>

      <section className="dash-card dash-asked" aria-labelledby="dash-asked-title">
        <div className="dash-card-head">
          <h2 id="dash-asked-title">Recently asked</h2>
          <span className="muted">Reported by 1on1 learners</span>
        </div>
        {reports.data?.length ? (
          <ul>
            {reports.data.map((r) => (
              <li key={r.questionId + r.company}>
                <Link to={"/practice/q/" + r.questionId}>{r.title}</Link>
                <span className="dash-chip">{r.company}</span>
                <small>
                  {r.stage === "OA" ? "Online assessment" : "Interview"}, {monthName(r.month)}
                  {r.reports > 1 ? `, ${r.reports} learners` : ""}
                </small>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">
            No reports yet. When you meet a question in an assessment or interview, open it and press "I was asked this". Until then,
            the <Link to="/practice?tab=companies">company lists</Link> show older community data.
          </p>
        )}
      </section>

      <section className="dash-links" aria-label="Go to">
        {LINKS.map(([to, label, key, Icon]) => (
          <Link key={to} to={to}>
            <Icon size={18} aria-hidden="true" />
            <span>{label}</span>
            <kbd aria-hidden="true">{key}</kbd>
          </Link>
        ))}
      </section>
    </div>
  );
}
