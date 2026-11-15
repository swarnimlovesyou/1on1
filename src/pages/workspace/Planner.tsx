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
              {plan.selected.map((choice, i) => {
                const p = problems.data?.find((p) => p.id === choice.id);
                return (
                  <div key={choice.id} className="plan-question">
                    {i % plan.perDay === 0 && (
                      <h3>Day {Math.floor(i / plan.perDay) + 1}</h3>
                    )}
                    <Link to={"/practice/" + choice.id}>
                      <span
                        className={
                          progress.solved.includes(choice.id) ? "success" : ""
                        }
                      >
                        {progress.solved.includes(choice.id) ? (
                          <CheckCircle size={20} />
                        ) : (
                          <Code size={20} />
                        )}
                      </span>
                      <div>
                        <strong>{p?.title ?? choice.id}</strong>
                        <p>Adds {choice.adds.join(" · ")}</p>
                      </div>
                      <ArrowUpRight size={18} />
                    </Link>
                  </div>
                );
              })}
              <details className="plan-method">
                <summary>Why these questions?</summary>
                <p>
                  Greedy set cover chooses the question adding the most
                  uncovered topics at each step. Ties use stable problem
                  identifiers. It gives a compact approximation rather than a
                  guaranteed minimum. Daily grouping follows your chosen
                  question count.
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
