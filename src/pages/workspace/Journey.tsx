import { Link } from "react-router-dom";
import { ArrowRight, CalendarCheck, Compass, Path as PathIcon } from "@phosphor-icons/react";
import { useApp } from "../../context";
import { useLearningMap } from "../LearningMap";
import { useLessons } from "../Learning";
import { FAMILIES, familyOfLesson, type FamilyId } from "../../families";
import type { EvidenceState, MapConcept, Plan } from "../../types";

const STATES: { id: EvidenceState; label: string }[] = [
  { id: "accepted", label: "Solved a problem" },
  { id: "passed", label: "Passed the check" },
  { id: "explored", label: "Explored" },
  { id: "new", label: "Not started" },
];

/** Concepts not started whose prerequisites all have some evidence: the learner's frontier. */
export function frontier(concepts: MapConcept[]): MapConcept[] {
  const byId = new Map(concepts.map((c) => [c.id, c]));
  return concepts
    .filter((c) => c.state === "new" && c.prerequisites.every((p) => (byId.get(p)?.state ?? "new") !== "new"))
    .sort((a, b) => a.order - b.order);
}

/** Remaining, overdue and finishing date for a plan's dated tasks, as of today (YYYY-MM-DD). */
export function forecast(plan: Plan, today: string) {
  const open = (plan.tasks ?? []).filter((t) => !t.done);
  return {
    done: (plan.tasks ?? []).length - open.length,
    total: (plan.tasks ?? []).length,
    overdue: open.filter((t) => t.date < today).length,
    finish: open.map((t) => t.date).sort().at(-1),
  };
}

/** The most recently created plan; plans arrive ordered by id, not by date. */
export function latestPlan(plans: Plan[]): Plan | undefined {
  return [...plans].sort((a, b) => (a.createdAt ?? "").localeCompare(b.createdAt ?? "")).at(-1);
}

/** What the learner has done, by concept and family, and where they are heading next. */
export default function Journey() {
  const { progress } = useApp();
  const map = useLearningMap();
  const lessons = useLessons();
  const concepts = map.data?.concepts ?? [];
  if (!concepts.length) return null;
  const counts = STATES.map((s) => ({ ...s, n: concepts.filter((c) => c.state === s.id).length }));
  const next = map.data!.nextAction;
  const ahead = frontier(concepts).slice(0, 3);
  const plan = latestPlan(progress.plans);
  const f = plan && forecast(plan, map.data!.today);
  const families = (Object.keys(FAMILIES) as FamilyId[])
    .map((id) => {
      const members = (lessons.data ?? []).filter((l) => familyOfLesson(l) === id);
      return { id, total: members.length, done: members.filter((l) => progress.completed.includes(l.id)).length };
    })
    .filter((x) => x.total);
  return (
    <section className="journey">
      <div className="journey-done">
        <h2>Where you've been</h2>
        <div className="mastery-bar" role="img" aria-label={counts.map((c) => `${c.label}: ${c.n}`).join(", ")}>
          {counts.map((c) => c.n > 0 && <span key={c.id} className={"m-" + c.id} style={{ flexGrow: c.n }} />)}
        </div>
        <ul className="mastery-legend">
          {counts.map((c) => (
            <li key={c.id}>
              <i className={"m-" + c.id} aria-hidden="true" />
              {c.label} <strong>{c.n}</strong>
            </li>
          ))}
        </ul>
        <ul className="family-progress">
          {families.map((x) => (
            <li key={x.id}>
              <span>{FAMILIES[x.id].label}</span>
              <progress max={x.total} value={x.done} aria-label={`${FAMILIES[x.id].label}: ${x.done} of ${x.total} explored`} />
              <small>
                {x.done} / {x.total}
              </small>
            </li>
          ))}
        </ul>
      </div>
      <div className="journey-ahead">
        <h2>Where you're heading</h2>
        <Link className="journey-next" to={next.href}>
          <Compass size={20} aria-hidden="true" />
          <span>
            <strong>{next.title}</strong>
            <small>{next.reason}</small>
          </span>
          <ArrowRight size={16} aria-hidden="true" />
        </Link>
        {!!ahead.length && (
          <>
            <h3>
              <PathIcon size={16} aria-hidden="true" /> Ready to open next
            </h3>
            <ol className="journey-frontier">
              {ahead.map((c) => (
                <li key={c.id}>
                  <Link to={c.lessonIds[0] ? "/learn/" + c.lessonIds[0] : "/learn"}>{c.title}</Link>
                  <small>{c.prerequisites.length ? "Its prerequisites are underway" : "No prerequisites"}</small>
                </li>
              ))}
            </ol>
          </>
        )}
        {plan && f && f.total > 0 && (
          <div className="journey-plan">
            <CalendarCheck size={18} aria-hidden="true" />
            <div>
              <strong>{plan.title}</strong>
              <small>
                {f.done} of {f.total} tasks done
                {f.finish && f.finish < map.data!.today
                  ? ", every remaining task is overdue"
                  : f.finish ? `, on course to finish ${new Date(f.finish + "T00:00:00Z").toLocaleDateString(undefined, { day: "numeric", month: "short", timeZone: "UTC" })}` : ", complete"}
                {f.overdue ? `; ${f.overdue} overdue` : ""}
              </small>
              <progress max={f.total} value={f.done} aria-hidden="true" />
            </div>
            <Link to="/plan">Open</Link>
          </div>
        )}
      </div>
    </section>
  );
}
