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
interface Cohort {
  id: string;
  name: string;
  code: string;
  members: { id: string; name: string; score: number; solved: number; week: number }[];
  weeklyProblem?: { id?: string; title?: string; difficulty?: string; solvedBy?: string[] };
  quartiles: { q1?: number; median?: number; q3?: number };
}
export function Cohorts() {
  return (
    <Gate>
      <CohortContent />
    </Gate>
  );
}
function CohortContent() {
  const { user, notify } = useApp(),
    qc = useQueryClient(),
    [name, setName] = useState(""),
    [code, setCode] = useState("");
  const q = useQuery({
    queryKey: ["cohorts"],
    queryFn: () => api<Cohort[]>("/cohorts"),
  });
  const mutate = useMutation({
    mutationFn: ({ join }: { join: boolean }) =>
      api("/cohorts" + (join ? "/join" : ""), join ? { code } : { name }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["cohorts"] });
      setName("");
      setCode("");
    },
    onError: (e) => notify(e.message),
  });
  return (
    <>
      <PageHeading
        title="Better questions. Together."
        description="Make a small space for your study group to keep moving."
      />
      <div className="cohort-forms">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutate.mutate({ join: false });
          }}
        >
          <h2>Start a study circle.</h2>
          <p>Invite classmates with a private code.</p>
          <label>
            Cohort name
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="The Tuesday study group"
              required
              maxLength={100}
            />
          </label>
          <button className="button primary small" disabled={mutate.isPending}>
            <Plus size={16} />
            Create cohort
          </button>
        </form>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutate.mutate({ join: true });
          }}
        >
          <h2>Pull up a chair.</h2>
          <p>Already have an invitation?</p>
          <label>
            Invitation code
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="8-character code"
              required
            />
          </label>
          <button
            className="button secondary small"
            disabled={mutate.isPending}
          >
            Join a cohort <ArrowRight size={16} />
          </button>
        </form>
      </div>
      {q.isLoading ? (
        <Loading />
      ) : q.error ? (
        <ErrorState error={q.error} />
      ) : q.data?.length ? (
        q.data.map((c) => (
          <section className="cohort-board" key={c.id}>
            <div className="section-heading">
              <h2>{c.name}</h2>
              <button
                className="button secondary small"
                onClick={() => {
                  navigator.clipboard.writeText(c.code);
                  notify("Invitation code copied");
                }}
              >
                Invite code: <code>{c.code}</code>
              </button>
            </div>
            <p className="muted">
              Native accepted problems earn 1 / 3 / 5 points for easy / medium /
              hard. Each problem counts once.
            </p>
            {c.weeklyProblem?.id && (
              <Link className="circle-weekly" to={"/practice/" + c.weeklyProblem.id}>
                <span className="muted">This week's circle problem</span>
                <strong>{c.weeklyProblem.title}</strong>
                <span className={"difficulty " + c.weeklyProblem.difficulty?.toLowerCase()}>{c.weeklyProblem.difficulty}</span>
                <small>
                  {c.weeklyProblem.solvedBy?.length
                    ? "Solved by " + c.weeklyProblem.solvedBy.join(", ")
                    : "Nobody in the circle has solved it yet. Be the first."}
                </small>
              </Link>
            )}
            <ol className="circle-members">
              {c.members.map((m, i) => (
                <li key={m.id} className={m.id === user?.id ? "me" : ""}>
                  <span className="circle-rank">{i + 1}</span>
                  <span className="circle-avatar" aria-hidden="true">
                    {m.name
                      .split(/\s+/)
                      .map((w) => w[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </span>
                  <span className="circle-name">
                    {m.name}
                    {m.id === user?.id && <span className="you-label">You</span>}
                    <small>
                      {m.solved} solved, {m.week} learning {m.week === 1 ? "action" : "actions"} this week
                    </small>
                  </span>
                  <span className="circle-score">
                    <strong>{m.score}</strong>
                    <progress max={Math.max(1, c.members[0].score)} value={m.score} aria-label={`${m.name}: ${m.score} points`} />
                  </span>
                </li>
              ))}
            </ol>
            {c.quartiles.median !== undefined ? (
              <p className="cohort-quartiles">
                Cohort thresholds · lower quartile {c.quartiles.q1} · median{" "}
                {c.quartiles.median} · upper quartile {c.quartiles.q3}
                <small>
                  Computed with randomized Quickselect; these describe activity,
                  not mastery.
                </small>
              </p>
            ) : (
              <p className="muted">
                Quartile summaries appear when at least five members join.
              </p>
            )}
          </section>
        ))
      ) : (
        <div className="empty">
          <Users size={42} />
          <h2>Room for your people.</h2>
          <p>Your cohorts will appear here when you create or join one.</p>
        </div>
      )}
    </>
  );
}
