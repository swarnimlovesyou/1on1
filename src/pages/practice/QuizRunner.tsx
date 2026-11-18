import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../../context";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle, XCircle } from "@phosphor-icons/react";
import { api } from "../../api";
import { clock } from "./mockTime";

type Question = { id: string; section: string; prompt: string; options?: string[]; unit?: string };
type Quiz = { id: string; minutes: number; deadline: string; questions: Question[] };
type Review = { id: string; section: string; prompt: string; given: string; expected: string; correct: boolean; explanation: string };
type Result = { score: number; total: number; late: boolean; sections: { section: string; score: number; total: number }[]; review: Review[] };

/** Timed quiz: aptitude, reasoning and CS fundamentals, one question at a time; graded on the server. */
export default function QuizRunner() {
  const { user } = useApp();
  const autoSubmitted = useRef("");
  const [size, setSize] = useState(15);
  const [minutes, setMinutes] = useState(20);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [at, setAt] = useState(0);
  const [confirm, setConfirm] = useState(false);
  const [now, setNow] = useState(Date.now());
  const start = useMutation({ mutationFn: () => api<Quiz>("/quizzes", { questions: size, minutes }), onSuccess: () => (setAnswers({}), setAt(0)) });
  const submit = useMutation({ mutationFn: (id: string) => api<Result>(`/quizzes/${id}/submit`, { answers }) });
  const quiz = start.data;
  const left = quiz ? Math.max(0, Math.round((new Date(quiz.deadline).getTime() - now) / 1000)) : 0;

  useEffect(() => {
    if (!quiz || submit.data) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [quiz, submit.data]);
  useEffect(() => {
    // time is up: submit once per quiz, even if that request fails
    if (quiz && left === 0 && autoSubmitted.current !== quiz.id) {
      autoSubmitted.current = quiz.id;
      submit.mutate(quiz.id);
    }
  }, [left, quiz, submit]);

  if (!user)
    return (
      <div className="empty">
        <h2>Sign in to take a timed quiz.</h2>
        <p>Your attempt is graded on the server and kept with your account.</p>
        <Link className="button primary small" to="/login">
          Sign in
        </Link>
      </div>
    );

  if (submit.data) {
    const r = submit.data;
    return (
      <section className="quiz-result">
        <h2>
          {r.score} of {r.total}
        </h2>
        <p className="muted">{r.late ? "Submitted after the time ran out." : "Your answers were checked on the server."}</p>
        <div className="quiz-sections">
          {r.sections.map((s) => (
            <div key={s.section} className="quiz-section-score">
              <span>{s.section}</span>
              <strong>
                {s.score} / {s.total}
              </strong>
              <progress max={s.total} value={s.score} aria-hidden="true" />
            </div>
          ))}
        </div>
        <ol className="quiz-review">
          {r.review.map((q) => (
            <li key={q.id} className={q.correct ? "right" : "wrong"}>
              <span className="quiz-mark">{q.correct ? <CheckCircle size={18} weight="fill" /> : <XCircle size={18} weight="fill" />}</span>
              <div>
                <small>{q.section}</small>
                <p className="quiz-review-prompt">{q.prompt}</p>
                <p>
                  {q.correct ? "Correct." : <>Answer: <strong>{q.expected}</strong>{q.given ? <> (you said {q.given})</> : " (not answered)"}</>}
                </p>
                <p className="muted">{q.explanation}</p>
              </div>
            </li>
          ))}
        </ol>
        <button className="button primary" type="button" onClick={() => (submit.reset(), start.reset())}>
          Take another quiz
        </button>
      </section>
    );
  }

  if (!quiz)
    return (
      <section className="quiz-setup">
        <h2>Aptitude, reasoning and CS fundamentals, on a clock</h2>
        <p className="muted">A third of the questions from each section, freshly generated or drawn from the fact-checked guides. Answers are revealed only when you submit.</p>
        <div className="quiz-choices">
          <label>
            Questions
            <select value={size} onChange={(e) => setSize(Number(e.target.value))}>
              <option value={15}>15</option>
              <option value={30}>30</option>
            </select>
          </label>
          <label>
            Time
            <select value={minutes} onChange={(e) => setMinutes(Number(e.target.value))}>
              <option value={20}>20 minutes</option>
              <option value={40}>40 minutes</option>
            </select>
          </label>
          <button className="button primary" type="button" disabled={start.isPending} onClick={() => start.mutate()}>
            Start the quiz
          </button>
        </div>
        {start.error && (
          <p className="inline-alert" role="alert">
            {start.error.message}
          </p>
        )}
      </section>
    );

  const q = quiz.questions[at];
  const answered = (id: string) => !!answers[id]?.trim();
  const set = (value: string) => setAnswers((a) => ({ ...a, [q.id]: value }));
  const unanswered = quiz.questions.filter((x) => !answered(x.id)).length;
  return (
    <section className="quiz-runner" data-no-shortcuts>
      <div className="quiz-top">
        <span className="quiz-section">{q.section}</span>
        <span className={"quiz-timer" + (left < 60 ? " low" : "")} role="timer" aria-label="Time left">
          {clock(left)}
        </span>
      </div>
      <nav className="quiz-nav" aria-label="Questions">
        {quiz.questions.map((x, i) => (
          <button
            key={x.id}
            type="button"
            className={(i === at ? "current " : "") + (answered(x.id) ? "answered" : "")}
            aria-current={i === at ? "step" : undefined}
            aria-label={`Question ${i + 1}${answered(x.id) ? ", answered" : ""}`}
            onClick={() => setAt(i)}
          >
            {i + 1}
          </button>
        ))}
      </nav>
      <div className="quiz-card">
        <p className="quiz-question">{q.prompt}</p>
        {q.options ? (
          <div className="quiz-options checkpoint-options" role="group" aria-label="Choices">
            {q.options.map((o, i) => (
              <button key={o} type="button" className={answers[q.id] === o ? "selected" : ""} aria-pressed={answers[q.id] === o} onClick={() => set(o)}>
                <span>{String.fromCharCode(65 + i)}</span>
                {o}
              </button>
            ))}
          </div>
        ) : (
          <label className="drill-answer">
            <input aria-label="Your answer" value={answers[q.id] ?? ""} onChange={(e) => set(e.target.value)} autoComplete="off" />
            {q.unit && <span>{q.unit}</span>}
          </label>
        )}
      </div>
      <div className="challenge-actions">
        <button className="button" type="button" disabled={at === 0} onClick={() => setAt(at - 1)}>
          Previous
        </button>
        <button className="button" type="button" disabled={at === quiz.questions.length - 1} onClick={() => setAt(at + 1)}>
          Next
        </button>
        <button className="button primary" type="button" onClick={() => (unanswered ? setConfirm(true) : submit.mutate(quiz.id))} disabled={submit.isPending}>
          Submit
        </button>
      </div>
      {confirm && (
        <div className="quiz-confirm" role="alertdialog" aria-label="Submit with unanswered questions">
          <p>
            {unanswered} question{unanswered === 1 ? " is" : "s are"} still unanswered.
          </p>
          <button className="button" type="button" autoFocus onClick={() => setConfirm(false)}>
            Keep going
          </button>
          <button className="button primary" type="button" onClick={() => (setConfirm(false), submit.mutate(quiz.id))}>
            Submit anyway
          </button>
        </div>
      )}
      {submit.error && (
        <p className="inline-alert" role="alert">
          {submit.error.message}
        </p>
      )}
    </section>
  );
}
