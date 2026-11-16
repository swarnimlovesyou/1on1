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
import type { Note, Plan, PlanTask, User } from "../../types";
import { ReviewsDue } from "../LearningMap";
import { useLessons, useProblems } from "../Learning";
import {
  Loading,
  ErrorState,
  PageHeading,
  Gate,
} from "../../components/Shared";
import Experiment from "../../components/Experiment";
export function Planner() {
  return (
    <Gate>
      <PlanContent />
    </Gate>
  );
}
function PlanContent() {
  const { progress, reload, notify } = useApp(),
    problems = useProblems(),
    [topics, setTopics] = useState<string[]>(["Arrays", "Dynamic programming"]),
    [difficulty, setDifficulty] = useState("All"),
    [perDay, setPerDay] = useState(2),
    [title, setTitle] = useState("My next chapter"),
    [active, setActive] = useState<Plan>();
  const create = useMutation({
    mutationFn: () =>
      api<Plan>("/plans", { topics, difficulty, perDay, title }),
    onSuccess: (p) => {
      setActive(p);
      reload();
      notify("Your practice plan is ready");
    },
  });
  const choices = [...new Set(problems.data?.flatMap((p) => p.topics))];
  const plan = active ?? progress.plans.at(-1);
  return (
    <>
      <PageHeading
        title="A little direction goes a long way."
        description="Choose what you want to understand. We’ll connect it to a purposeful set of problems."
      />
      <ReviewsDue />
      <div className="planner-layout">
        <section className="plan-builder">
          <h2>What’s your next chapter?</h2>
          <label>
            Give your plan a name
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
          </label>
          <label>Topics to work on</label>
          <div className="selectable-topics">
            {choices.map((t) => (
              <button
                className={topics.includes(t) ? "selected" : ""}
                key={t}
                onClick={() =>
                  setTopics((v) =>
                    v.includes(t) ? v.filter((x) => x !== t) : [...v, t],
                  )
                }
              >
                {topics.includes(t) && <Check size={14} />} {t}
              </button>
            ))}
          </div>
          <div className="form-row">
            <label>
              Difficulty
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                {["All", "Easy", "Medium", "Hard"].map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </label>
            <label>
              Problems per day
              <input
                type="number"
                min={1}
                max={10}
                value={perDay}
                onChange={(e) => setPerDay(+e.target.value)}
              />
            </label>
          </div>
          <button
            className="button primary full"
            disabled={!topics.length || create.isPending}
            onClick={() => create.mutate()}
          >
            {create.isPending
              ? "Finding the connections…"
              : "Build my practice plan"}
            <ArrowRight size={17} />
          </button>
          {create.error && <ErrorState error={create.error} />}
          <p className="form-note">
            Already solved problems are excluded. Select fewer topics for a
            smaller plan.
          </p>
        </section>
        <section className="plan-result">
          {plan ? (
            <>
              <div className="section-heading">
                <div>
                  <span className="muted">Your practice plan</span>
                  <h2>{plan.title}</h2>
                </div>
                <span className="chip">{plan.selected.length} questions</span>
              </div>
              <div className="coverage-summary">
                <CheckCircle size={20} />
                <span>
                  {plan.topics.length - plan.uncovered.length} of{" "}
                  {plan.topics.length} topics covered
                </span>
              </div>
              {plan.uncovered.length > 0 && (
                <p className="inline-alert">
                  No eligible questions cover: {plan.uncovered.join(", ")}.
                  Broaden the difficulty filter or add content.
                </p>
              )}
              <PlanTasks plan={plan} onChange={setActive} />
              <details className="plan-method">
                <summary>Why these questions?</summary>
                <p>
                  Greedy set cover chooses the question adding the most
                  uncovered topics at each step. Ties use stable problem
                  identifiers. It gives a compact approximation rather than a
                  guaranteed minimum. The questions become dated tasks, your
                  chosen number per day. Re-planning keeps every task you
                  completed and only re-dates the rest.
                </p>
              </details>
            </>
          ) : (
            <div className="empty">
              <CalendarBlank size={42} />
              <h2>Less wondering what to do next.</h2>
              <p>
                Your plan will show how each question adds to the topics you
                want to cover.
              </p>
            </div>
          )}
        </section>
      </div>
      {progress.plans.length > 1 && (
        <section className="saved-plans">
          <h2>Earlier plans</h2>
          {progress.plans
            .slice()
            .reverse()
            .map((p) => (
              <button
                className="saved-plan"
                key={p.id}
                onClick={() => setActive(p)}
              >
                <CalendarBlank size={19} />
                <span>{p.title}</span>
                <small>{p.selected.length} questions</small>
                <ArrowRight size={16} />
              </button>
            ))}
        </section>
      )}
    </>
  );
}

/** The plan as dated tasks: tick off, move, or re-plan the unfinished ones from a new start date. */
function PlanTasks({ plan, onChange }: { plan: Plan; onChange: (p: Plan) => void }) {
  const { progress, reload, notify } = useApp(),
    problems = useProblems(),
    today = new Date().toISOString().slice(0, 10),
    [from, setFrom] = useState(today),
    [perDay, setPerDay] = useState(plan.perDay);
  const saved = (p: Plan, message?: string) => {
    onChange(p);
    reload();
    if (message) notify(message);
  };
  const update = useMutation({
    mutationFn: ({ task, body }: { task: PlanTask; body: { done?: boolean; date?: string } }) =>
      api<Plan>(`/plans/${plan.id}/tasks/${task.id}`, body, "PATCH"),
    onSuccess: (p) => saved(p),
  });
  const replan = useMutation({
    mutationFn: () => api<Plan>(`/plans/${plan.id}/regenerate`, { startDate: from, perDay }),
    onSuccess: (p) => saved(p, "Unfinished work re-planned; completed tasks kept"),
  });
  const tasks = plan.tasks ?? [];
  const days = [...new Set(tasks.map((t) => t.date))];
  return (
    <>
      {!tasks.length && (
        <p className="inline-alert">
          This plan was made before plans had dates. Re-plan it to turn its
          questions into dated tasks.
        </p>
      )}
      {days.map((day) => (
        <div key={day} className="plan-day">
          <h3>
            {day === today ? "Today" : new Date(day + "T00:00:00").toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}
            {day < today && tasks.some((t) => t.date === day && !t.done) && <span className="chip">overdue</span>}
          </h3>
          {tasks
            .filter((t) => t.date === day)
            .map((t) => {
              const p = problems.data?.find((x) => x.id === t.problemId),
                accepted = progress.solved.includes(t.problemId);
              return (
                <div key={t.id} className={"plan-task" + (t.done ? " done" : "")}>
                  <input
                    type="checkbox"
                    checked={t.done}
                    disabled={update.isPending}
                    aria-label={(t.done ? "Reopen " : "Mark done: ") + (p?.title ?? t.problemId)}
                    onChange={() => update.mutate({ task: t, body: { done: !t.done } })}
                  />
                  <Link to={"/practice/" + t.problemId}>
                    <strong>{p?.title ?? t.problemId}</strong>
                    <small>
                      Adds {t.adds.join(" · ")}
                      {accepted && " · accepted by the judge"}
                    </small>
                  </Link>
                  <input
                    type="date"
                    value={t.date}
                    disabled={t.done || update.isPending}
                    aria-label={"Move " + (p?.title ?? t.problemId)}
                    onChange={(e) => e.target.value && update.mutate({ task: t, body: { date: e.target.value } })}
                  />
                </div>
              );
            })}
        </div>
      ))}
      {(update.error || replan.error) && <ErrorState error={update.error ?? replan.error} />}
      <div className="replan">
        <label>
          Re-plan unfinished work from
          <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
        </label>
        <label>
          Per day
          <input type="number" min={1} max={10} value={perDay} onChange={(e) => setPerDay(+e.target.value)} />
        </label>
        <button className="button" disabled={replan.isPending || !from} onClick={() => replan.mutate()}>
          <ArrowClockwise size={16} /> {replan.isPending ? "Re-planning…" : "Re-plan"}
        </button>
      </div>
    </>
  );
}
