import { useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, CheckCircle } from "@phosphor-icons/react";
import { api } from "../../api";
import { Loading, ErrorState } from "../../components/Shared";
import { usePrep } from "./usePrep";
import { nextStreak } from "./streak";

type Question = { topic: string; seed: number; prompt: string; options?: string[]; unit?: string };
type Result = { correct: boolean; expected: string; explanation: string };

/** One page per topic: a new topic starts with a clean answer, result and streak. */
export default function DrillRoute() {
  const { topic = "" } = useParams();
  return <DrillPage key={topic} topic={topic} />;
}

/** Unlimited generated questions for one aptitude or reasoning topic, graded on the server. */
function DrillPage({ topic }: { topic: string }) {
  const prep = usePrep();
  const [round, setRound] = useState(0);
  const [answer, setAnswer] = useState("");
  const [streak, setStreak] = useState(0);
  // each visit gets its own cache key, so coming back to a drill always fetches a fresh question
  const [visit] = useState(() => Math.random());
  const question = useQuery({
    queryKey: ["drill", topic, visit, round],
    queryFn: () => api<Question>(`/drills/${topic}/next`),
    staleTime: Infinity,
    gcTime: 0,
    placeholderData: (previous) => previous, // keep the card on screen while the next question loads
    retry: false,
  });
  const check = useMutation({
    mutationFn: (q: Question) => api<Result>(`/drills/${topic}/answer`, { seed: q.seed, answer }),
    onSuccess: (r) => setStreak((s) => nextStreak(s, r.correct)),
  });
  const guide = prep.data?.guides.find((g) => g.drill === topic);

  const back = (
    <Link className="back-link" to={guide ? "/prep/guide/" + guide.id : "/prep"}>
      <ArrowLeft size={16} aria-hidden="true" />
      {guide ? "Back to the guide" : "All of Prep"}
    </Link>
  );
  if (question.isLoading) return <Loading />;
  if (question.error || !question.data)
    return (
      <article className="prep-guide drill">
        {back}
        <ErrorState error={question.error} retry={() => question.refetch()} />
      </article>
    );
  const q = question.data;
  const unit = (value: string) => (q.unit === "₹" ? "₹" + value : q.unit === "%" ? value + "%" : q.unit ? `${value} ${q.unit}` : value);
  const loadingNext = question.isPlaceholderData;

  function submit(event: FormEvent) {
    event.preventDefault();
    if (answer.trim() && !check.isPending && !check.data && !loadingNext) check.mutate(q);
  }
  function next() {
    setAnswer("");
    check.reset();
    setRound((r) => r + 1);
  }

  return (
    <article className="prep-guide drill">
      {back}
      <h1 className="display">{guide ? guide.title : "Practice"}</h1>
      <p className="muted">
        A new question every time, checked on the server. <span className="drill-streak">Streak: {streak}</span>
      </p>
      <form className="drill-card" onSubmit={submit}>
        <p className="drill-prompt">{q.prompt}</p>
        {q.options ? (
          <div className="checkpoint-options" role="group" aria-label="Choices">
            {q.options.map((option, index) => (
              <button
                key={option}
                type="button"
                aria-pressed={answer === option}
                className={answer === option ? "selected" : ""}
                disabled={!!check.data}
                onClick={() => setAnswer(option)}
              >
                <span>{String.fromCharCode(65 + index)}</span>
                {option}
              </button>
            ))}
          </div>
        ) : (
          <label className="drill-answer">
            {q.unit === "₹" && <span aria-hidden="true">₹</span>}
            <input
              aria-label="Your answer"
              value={answer}
              disabled={!!check.data}
              autoComplete="off"
              onChange={(e) => setAnswer(e.target.value)}
            />
            {q.unit && q.unit !== "₹" && <span>{q.unit}</span>}
          </label>
        )}
        <div className="challenge-actions">
          {!check.data && (
            <button className="button primary" type="submit" disabled={!answer.trim() || check.isPending}>
              Check
            </button>
          )}
          <button className="button" type="button" onClick={next} disabled={check.isPending || loadingNext}>
            Next question
            <ArrowRight size={16} aria-hidden="true" />
          </button>
        </div>
        {check.error && (
          <p className="inline-alert" role="alert">
            {check.error.message}
          </p>
        )}
        {check.data && (
          <div className={"challenge-feedback " + (check.data.correct ? "is-correct" : "")} role="status">
            {check.data.correct && <CheckCircle size={20} aria-hidden="true" />}
            <div>
              <p>{check.data.correct ? "Correct." : `Not quite. The answer is ${unit(check.data.expected)}.`}</p>
              <p>{check.data.explanation}</p>
            </div>
          </div>
        )}
      </form>
    </article>
  );
}
