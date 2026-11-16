import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle,
  ClockCounterClockwise,
  Code,
  Compass,
} from "@phosphor-icons/react";
import { api } from "../api";
import { useApp } from "../context";
import type { EvidenceState, LearningMap, MapConcept, NextAction } from "../types";
import { ErrorState, Loading } from "../components/Shared";

/** The concept map, due reviews and next action, refreshed whenever the learner's evidence changes. */
export function useLearningMap() {
  const { progress, user } = useApp();
  return useQuery({
    queryKey: [
      "learning-map",
      user?.id ?? "guest",
      progress.attempts?.length ?? 0,
      progress.solved.length,
      progress.completed.length,
      progress.plans.map((p) => (p.tasks ?? []).filter((t) => t.done).length).join(","),
    ],
    queryFn: () => api<LearningMap>("/learning-map"),
  });
}

const STATE_LABEL: Record<EvidenceState, string> = {
  new: "Not started",
  explored: "Explored",
  passed: "Challenge passed",
  accepted: "Problem accepted",
};

const ACTION_ICON = {
  review: ClockCounterClockwise,
  task: Code,
  learn: Compass,
  practice: Code,
  done: CheckCircle,
};

/** One clear thing to do next, with the reason behind it. */
export function NextActionCard({ action }: { action: NextAction }) {
  const Icon = ACTION_ICON[action.kind];
  return (
    <Link to={action.href} className={"next-action next-" + action.kind}>
      <span className="next-icon">
        <Icon size={22} />
      </span>
      <span className="next-copy">
        <small>Your next step</small>
        <strong>{action.title}</strong>
        <span>{action.reason}</span>
      </span>
      <ArrowRight size={18} />
    </Link>
  );
}

/** Longest prerequisite chain above each concept: its column in the map. */
function levels(concepts: MapConcept[]) {
  const level = new Map<string, number>();
  for (const c of concepts) // concepts arrive in prerequisite order, so every prerequisite is already placed
    level.set(c.id, Math.max(-1, ...c.prerequisites.map((p) => level.get(p) ?? 0)) + 1);
  return level;
}

const W = 196, H = 62, GX = 52, GY = 12;

/** A freely explorable map: prerequisite layers with links, plus an accessible list on small screens. */
export function ConceptMap() {
  const map = useLearningMap();
  if (map.isLoading) return <Loading />;
  if (map.error || !map.data)
    return <ErrorState error={map.error} retry={() => map.refetch()} />;
  const { concepts } = map.data;
  const level = levels(concepts);
  const rows = new Map<number, number>();
  const at = new Map<string, { x: number; y: number }>();
  for (const c of concepts) {
    const l = level.get(c.id)!, r = rows.get(l) ?? 0;
    rows.set(l, r + 1);
    at.set(c.id, { x: l * (W + GX), y: r * (H + GY) });
  }
  const width = (Math.max(...level.values()) + 1) * (W + GX) - GX;
  const height = Math.max(...rows.values()) * (H + GY) - GY;
  const byId = new Map(concepts.map((c) => [c.id, c]));
  return (
    <section className="concept-map-section">
      <NextActionCard action={map.data.nextAction} />
      <div className="map-legend" aria-label="What the colours mean">
        {(["new", "explored", "passed", "accepted"] as EvidenceState[]).map((s) => (
          <span key={s} className={"legend-" + s}>
            <i /> {STATE_LABEL[s]}
          </span>
        ))}
        <span className="legend-due">
          <i /> Review due
        </span>
      </div>
      <p className="map-note">
        Each grade is separate evidence: opening a notebook is exploring,
        a server-graded challenge is a pass, and only the judge accepting your
        code counts as solved. Nothing is locked; the arrows show what each
        concept builds on.
      </p>
      <div className="concept-map-scroll">
        <div className="concept-map" style={{ width, height }}>
          <svg width={width} height={height} aria-hidden="true">
            {concepts.flatMap((c) =>
              c.prerequisites.map((p) => {
                const a = at.get(p)!, b = at.get(c.id)!;
                const x1 = a.x + W, y1 = a.y + H / 2, x2 = b.x, y2 = b.y + H / 2;
                const mid = (x1 + x2) / 2;
                return (
                  <path
                    key={p + c.id}
                    className={byId.get(p)!.state === "new" ? "edge" : "edge edge-on"}
                    d={`M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2},${y2}`}
                  />
                );
              }),
            )}
          </svg>
          {concepts.map((c) => {
            const p = at.get(c.id)!;
            return (
              <Link
                key={c.id}
                to={c.lessonIds[0] ? "/learn/" + c.lessonIds[0] : "/learn"}
                className={"map-node state-" + c.state + (c.review?.due ? " due" : "")}
                style={{ left: p.x, top: p.y, width: W, height: H }}
                title={c.evidence.join(" ")}
              >
                <strong>{c.title}</strong>
                <small>
                  {STATE_LABEL[c.state]}
                  {c.review?.due ? " · review due" : ""}
                </small>
              </Link>
            );
          })}
        </div>
      </div>
      <ol className="concept-map-list">
        {concepts.map((c) => (
          <li key={c.id} className={"state-" + c.state}>
            <Link to={c.lessonIds[0] ? "/learn/" + c.lessonIds[0] : "/learn"}>
              <strong>{c.title}</strong>
              <small>
                {STATE_LABEL[c.state]}
                {c.review?.due ? " · review due" : ""}
              </small>
            </Link>
            {c.prerequisites.length > 0 && (
              <p>
                Builds on{" "}
                {c.prerequisites.map((p) => byId.get(p)!.title).join(", ")}
              </p>
            )}
            <ul>
              {c.evidence.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
    </section>
  );
}

/** Concepts whose spaced review is due, most overdue first. */
export function ReviewsDue() {
  const map = useLearningMap();
  const due = map.data?.reviewsDue ?? [];
  if (!due.length) return null;
  return (
    <section className="reviews-due">
      <div className="section-heading">
        <h2>Due for review</h2>
        <span className="chip">{due.length}</span>
      </div>
      <p className="form-note">
        Answer one of its challenges without the hint to move it further out:
        1, then 3, then 7 days. A miss brings it back tomorrow.
      </p>
      {due.map((r) => (
        <Link
          key={r.conceptId}
          to={r.missed ? `/learn/${r.missed.lessonId}#checkpoint` : r.lessonId ? "/learn/" + r.lessonId : "/learn"}
          className="review-row"
        >
          <ClockCounterClockwise size={19} />
          <span>
            <strong>{r.title}</strong>
            <small>
              {r.overdueDays > 0
                ? `Due ${r.overdueDays} day${r.overdueDays === 1 ? "" : "s"} ago`
                : "Due today"}
              {r.lastOutcome === "missed" ? " · missed last time" : ""}
              {r.notes.length > 0 && ` · ${r.notes.length} note${r.notes.length === 1 ? "" : "s"} of yours`}
            </small>
            {r.missed && <small>Retry “{r.missed.title}”</small>}
          </span>
          <ArrowRight size={16} />
        </Link>
      ))}
    </section>
  );
}
