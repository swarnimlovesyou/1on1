import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Plus,
  Check,
  CheckCircle,
  Trash,
  BookmarkSimple,
  Notebook,
  CalendarBlank,
  ChartBar,
  Users,
  Plugs,
  ArrowClockwise,
  Download,
  Flask,
  ShieldCheck,
  ArrowLeft,
  Code,
  Lightbulb,
} from "@phosphor-icons/react";
import { api, download, resetCsrf } from "../../api";
import { useApp } from "../../context";
import type { Note, Plan, User } from "../../types";
import { useLessons, useProblems } from "../Learning";
import {
  Loading,
  ErrorState,
  PageHeading,
  Gate,
} from "../../components/Shared";
import Experiment from "../../components/Experiment";
import Journey from "./Journey";
export function Analytics() {
  return (
    <Gate>
      <AnalyticsContent />
    </Gate>
  );
}
function AnalyticsContent() {
  const cohorts = useQuery({
    queryKey: ["cohort-summaries"],
    queryFn: () =>
      api<
        {
          id: string;
          name: string;
          size: number;
          quartiles: { q1?: number; median?: number; q3?: number };
        }[]
      >("/cohorts/summary"),
  });
  const { progress } = useApp(),
    lessons = useLessons(),
    problems = useProblems();
  const dates = Array.from({ length: 98 }, (_, i) =>
    new Date(Date.now() - (97 - i) * 86400000).toISOString().slice(0, 10),
  );
  let streak = 0;
  const start = progress.activity[dates.at(-1)!] ? 0 : 1;
  for (let i = dates.length - 1 - start; i >= 0; i--) {
    if (progress.activity[dates[i]]) streak++;
    else break;
  }
  const topics = [...new Set(lessons.data?.flatMap((l) => l.topics))];
  return (
    <>
      <PageHeading
        title="Look how far you’re going."
        description="Your learning story is built from small, consistent moments."
      />
      <div className="progress-summary">
        <div>
          <span>Notebooks explored</span>
          <strong>
            {progress.completed.length}
            <small> / {lessons.data?.length ?? "…"}</small>
          </strong>
        </div>
        <div>
          <span>Problems solved here</span>
          <strong>
            {progress.solved.length}
            <small> / {problems.data?.length ?? "…"}</small>
          </strong>
        </div>
        <div>
          <span>Current study streak</span>
          <strong>
            {streak}
            <small> {streak === 1 ? "day" : "days"}</small>
          </strong>
        </div>
        <div>
          <span>Thoughts collected</span>
          <strong>{progress.notes.length}</strong>
        </div>
      </div>
      <Journey />
      <section className="activity-section">
        <div className="section-heading">
          <h2>Showing up counts.</h2>
          <span className="muted">The last 14 weeks · UTC</span>
        </div>
        <div
          className="heatmap"
          aria-label="Learning activity over the last 98 days"
        >
          {dates.map((day) => (
            <div
              key={day}
              tabIndex={0}
              className={
                "heat-cell level-" + Math.min(4, progress.activity[day] ?? 0)
              }
              title={`${day}: ${progress.activity[day] ?? 0} learning actions`}
              aria-label={`${day}: ${progress.activity[day] ?? 0} learning actions`}
            />
          ))}
        </div>
        <div className="heatmap-legend">
          <span>
            Every explored concept, saved thought, and learning update leaves a
            mark.
          </span>
          <span>
            Less <i />
            <i />
            <i />
            <i />
            <i /> More
          </span>
        </div>
      </section>
      {!!cohorts.data?.length && (
        <section className="cohort-summary-section">
          <div className="section-heading">
            <h2>Your study circles, at a glance.</h2>
            <Link to="/cohorts">
              Study together <ArrowRight size={16} />
            </Link>
          </div>
          {cohorts.data.map((c) => (
            <div className="cohort-summary-row" key={c.id}>
              <strong>{c.name}</strong>
              <span>{c.size} members</span>
              {c.quartiles.median !== undefined ? (
                <span>
                  Activity thresholds: {c.quartiles.q1} / {c.quartiles.median} /{" "}
                  {c.quartiles.q3}
                </span>
              ) : (
                <span>Quartiles appear at five members.</span>
              )}
            </div>
          ))}
          <p className="form-note">
            These score thresholds describe learning activity, not ability. Java
            computes the summary independently using randomized Quickselect; a
            full ranking is unnecessary.
          </p>
        </section>
      )}
      <section className="topic-progress">
        <div className="section-heading">
          <h2>A clearer picture, topic by topic.</h2>
          <Link to="/plan">
            Plan the next step <ArrowRight size={16} />
          </Link>
        </div>
        {topics.map((t) => {
          const ids =
              lessons.data
                ?.filter((l) => l.topics.includes(t))
                .map((l) => l.id) ?? [],
            done = ids.filter((id) => progress.completed.includes(id)).length,
            solved =
              problems.data?.filter(
                (p) => p.topics.includes(t) && progress.solved.includes(p.id),
              ).length ?? 0;
          return (
            <div className="topic-progress-row" key={t}>
              <strong>{t}</strong>
              <div className="progress-line">
                <span style={{ width: (100 * done) / ids.length + "%" }} />
              </div>
              <span>
                {done} / {ids.length} concepts
              </span>
              <small>{solved} solved</small>
            </div>
          );
        })}
      </section>
      <div className="quiet-callout">
        <Plugs size={24} />
        <div>
          <strong>Your LeetCode story belongs here too.</strong>
          <p>
            Connect your public profile to keep external practice beside your
            learning here.
          </p>
        </div>
        <Link to="/settings">
          Connect LeetCode <ArrowRight size={16} />
        </Link>
      </div>
    </>
  );
}
