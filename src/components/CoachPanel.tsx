import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Circle, Lightbulb, Warning } from "@phosphor-icons/react";
import { api } from "../api";
import type { CoachNudge, CoachView } from "../types";
import { useApp } from "../context";
import { Loading, ErrorState } from "./Shared";
import LinkedNotes from "./LinkedNotes";

const kindLabel: Record<CoachNudge["kind"], string> = {
  question: "A question first",
  evidence: "Look at the evidence",
  hint: "Hint",
  options: "Where to go from here",
  solution: "Worked solution",
};
const statusLabel: Record<string, string> = {
  ACCEPTED: "Accepted",
  WRONG_ANSWER: "Wrong answer",
  COMPILATION_ERROR: "Didn't compile",
  RUNTIME_ERROR: "Runtime error",
  TIME_LIMIT: "Too slow",
  QUEUED: "Waiting to run",
  RUNNING: "Running",
  UNAVAILABLE: "Runner unavailable",
  INTERRUPTED: "Interrupted",
};

/** Guided coding for one problem. Study support only: credit comes from accepted official runs. */
export default function CoachPanel({
  problem,
  language,
  refreshKey,
}: {
  problem: string;
  language: string;
  refreshKey: string;
}) {
  const { user, notify } = useApp();
  const qc = useQueryClient();
  const key = ["coach", problem, language];
  const view = useQuery({
    queryKey: key,
    queryFn: () =>
      api<CoachView>(
        `/coach/${problem}?language=${encodeURIComponent(language)}`,
      ),
    enabled: !!user,
  });
  // a finished run or a saved draft changes what the coach can say
  useEffect(() => {
    if (user) view.refetch();
  }, [refreshKey]);
  const update = (data: CoachView) => qc.setQueryData(key, data);
  const nudge = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api<CoachView>(`/coach/${problem}/nudge`, { language, ...body }),
    onSuccess: update,
    onError: (e) => notify(e.message),
  });
  const [confirming, setConfirming] = useState(false);

  if (!user)
    return (
      <p className="muted">
        Sign in to plan your approach and get coaching that remembers your
        progress.
      </p>
    );
  if (view.isLoading) return <Loading />;
  if (view.error || !view.data) return <ErrorState error={view.error} />;
  const v = view.data;
  const run = v.latestRun;
  const finished = v.stage === "done";

  return (
    <div className="coach">
      <ol className="coach-steps" aria-label="Your progress on this problem">
        {v.steps.map((s) => (
          <li key={s.key} className={s.done ? "done" : ""}>
            {s.done ? (
              <CheckCircle size={16} weight="fill" aria-hidden />
            ) : (
              <Circle size={16} aria-hidden />
            )}
            <span>{s.label}</span>
            <span className="sr-only">{s.done ? " (done)" : ""}</span>
          </li>
        ))}
      </ol>

      {!v.execution && (
        <p className="coach-note" role="status">
          <Warning size={16} aria-hidden />
          Runs aren’t available right now. Keep coaching going with hand
          checks; your draft is saved.
        </p>
      )}

      <PlanForm
        view={v}
        problem={problem}
        language={language}
        onSaved={update}
      />

      {run && (
        <div className={"coach-run" + (run.current ? "" : " stale")}>
          <strong>
            Latest run: {statusLabel[run.status] ?? run.status}
            {run.failing && !run.failing.public && run.status !== "ACCEPTED"
              ? ` on hidden case ${run.failing.index}`
              : ""}
          </strong>
          <span>
            {run.current
              ? "This is your current code."
              : "You’ve changed the code since this run, so run it again before relying on it."}
          </span>
        </div>
      )}

      {v.nudges.length > 0 && (
        <div className="coach-thread" aria-live="polite">
          {v.nudges.slice(-8).map((n) => (
            <div className={"coach-nudge kind-" + n.kind} key={n.at + n.kind}>
              <small>{kindLabel[n.kind]}</small>
              <p>{n.text}</p>
              {n.code && (
                <pre className="reference-code">{n.code}</pre>
              )}
            </div>
          ))}
        </div>
      )}

      {v.plan && (
        <div className="coach-actions">
          <button
            className="button primary small"
            disabled={nudge.isPending}
            onClick={() => nudge.mutate({})}
          >
            <Lightbulb size={16} />
            {v.nudges.length ? "Next nudge" : "Coach me"}
          </button>
          {!finished &&
            !v.accepted &&
            !v.solutionRevealed &&
            (confirming ? (
              <span className="coach-confirm">
                Show the full solution? It won’t mark this solved.
                <button
                  className="button secondary small"
                  onClick={() => {
                    setConfirming(false);
                    nudge.mutate({ want: "solution", confirm: true });
                  }}
                >
                  Show it
                </button>
                <button
                  className="button secondary small"
                  onClick={() => setConfirming(false)}
                >
                  Keep trying
                </button>
              </span>
            ) : (
              <button
                className="button secondary small"
                onClick={() => setConfirming(true)}
              >
                Show the worked solution
              </button>
            ))}
        </div>
      )}

      {(v.stage === "reflect" || v.stage === "done") && (
        <ReflectionForm
          view={v}
          problem={problem}
          language={language}
          onSaved={update}
        />
      )}
      <LinkedNotes problem={problem} />
    </div>
  );
}

function PlanForm({
  view,
  problem,
  language,
  onSaved,
}: {
  view: CoachView;
  problem: string;
  language: string;
  onSaved: (v: CoachView) => void;
}) {
  const { notify } = useApp();
  const [editing, setEditing] = useState(!view.plan);
  const [plan, setPlan] = useState({
    approach: view.plan?.approach ?? "",
    invariant: view.plan?.invariant ?? "",
    example: view.plan?.example ?? "",
  });
  const save = useMutation({
    mutationFn: () =>
      api<CoachView>(`/coach/${problem}/plan`, { language, ...plan }, "PUT"),
    onSuccess: (v) => {
      onSaved(v);
      setEditing(false);
    },
    onError: (e) => notify(e.message),
  });
  if (!editing && view.plan)
    return (
      <div className="coach-plan">
        <h3>Your plan</h3>
        <dl>
          <dt>Approach</dt>
          <dd>{view.plan.approach}</dd>
          <dt>What stays true</dt>
          <dd>{view.plan.invariant}</dd>
          <dt>Tiny example</dt>
          <dd>{view.plan.example}</dd>
        </dl>
        <button
          className="button secondary small"
          onClick={() => setEditing(true)}
        >
          Edit plan
        </button>
      </div>
    );
  return (
    <form
      className="coach-plan"
      onSubmit={(e) => {
        e.preventDefault();
        save.mutate();
      }}
    >
      <h3>Plan before you code</h3>
      <p>
        Explain your idea in your own words. The coach uses this plan to ask
        about your code later.
      </p>
      <label>
        Approach
        <textarea
          rows={3}
          maxLength={1500}
          required
          value={plan.approach}
          placeholder="Which values do you keep track of, and how do they change at each step?"
          onChange={(e) => setPlan({ ...plan, approach: e.target.value })}
        />
      </label>
      <label>
        What must stay true at every step
        <input
          maxLength={600}
          required
          value={plan.invariant}
          placeholder="After each step, best holds the largest total seen so far"
          onChange={(e) => setPlan({ ...plan, invariant: e.target.value })}
        />
      </label>
      <label>
        A tiny example, worked by hand
        <input
          maxLength={1000}
          required
          value={plan.example}
          placeholder="Input 3 1 2 gives 3 because…"
          onChange={(e) => setPlan({ ...plan, example: e.target.value })}
        />
      </label>
      <button className="button primary small" disabled={save.isPending}>
        Save plan
      </button>
    </form>
  );
}

function ReflectionForm({
  view,
  problem,
  language,
  onSaved,
}: {
  view: CoachView;
  problem: string;
  language: string;
  onSaved: (v: CoachView) => void;
}) {
  const { notify } = useApp();
  const [text, setText] = useState({
    complexity: view.reflection?.complexity ?? "",
    transfer: view.reflection?.transfer ?? "",
  });
  const save = useMutation({
    mutationFn: () =>
      api<CoachView>(
        `/coach/${problem}/reflection`,
        { language, ...text },
        "PUT",
      ),
    onSuccess: onSaved,
    onError: (e) => notify(e.message),
  });
  return (
    <form
      className="coach-plan"
      onSubmit={(e) => {
        e.preventDefault();
        save.mutate();
      }}
    >
      <h3>Accepted. Now make it stick.</h3>
      <label>
        How much work does your solution do, and why?
        <textarea
          rows={2}
          maxLength={800}
          required
          value={text.complexity}
          onChange={(e) => setText({ ...text, complexity: e.target.value })}
        />
      </label>
      <label>
        {view.transfer}
        <textarea
          rows={3}
          maxLength={1500}
          required
          value={text.transfer}
          onChange={(e) => setText({ ...text, transfer: e.target.value })}
        />
      </label>
      <button className="button primary small" disabled={save.isPending}>
        {view.reflection ? "Update reflection" : "Save reflection"}
      </button>
    </form>
  );
}
