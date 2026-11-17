import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle, Lightbulb } from "@phosphor-icons/react";
import { api } from "../../api";
import type { PrepGuide } from "../../types";

type Puzzle = NonNullable<PrepGuide["puzzle"]>;

/** A puzzle: the statement, hints revealed one at a time, the solution last, and an answer checked on the server. */
export default function PuzzleBlock({ id, puzzle }: { id: string; puzzle: Puzzle }) {
  const [hints, setHints] = useState(0);
  const [solution, setSolution] = useState(false);
  const [answer, setAnswer] = useState("");
  const check = useMutation({
    mutationFn: () => api<{ correct: boolean }>(`/prep/puzzles/${id}/check`, { answer }),
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    if (answer.trim() && !check.isPending) check.mutate();
  }
  return (
    <section className="puzzle">
      <h2>The puzzle</h2>
      <p className="prose preserve-lines puzzle-statement">{puzzle.statement}</p>
      {puzzle.checkable && (
        <form className="drill-answer" onSubmit={submit}>
          <input
            aria-label="Your answer"
            value={answer}
            autoComplete="off"
            onChange={(e) => {
              setAnswer(e.target.value);
              check.reset();
            }}
          />
          <button className="button primary" type="submit" disabled={!answer.trim() || check.isPending}>
            Check
          </button>
        </form>
      )}
      {check.error && (
        <p className="inline-alert" role="alert">
          {check.error.message}
        </p>
      )}
      {check.data && (
        <div className={"challenge-feedback " + (check.data.correct ? "is-correct" : "")} role="status">
          {check.data.correct && <CheckCircle size={20} aria-hidden="true" />}
          <p>{check.data.correct ? "Correct. Compare your reasoning with the solution below." : "Not quite. Try a hint before you look at the solution."}</p>
        </div>
      )}
      <ol className="puzzle-hints">
        {puzzle.hints.slice(0, hints).map((h, i) => (
          <li key={i}>
            <Lightbulb size={17} aria-hidden="true" /> {h}
          </li>
        ))}
      </ol>
      <div className="challenge-actions">
        {hints < puzzle.hints.length && (
          <button className="button" type="button" onClick={() => setHints((n) => n + 1)}>
            {hints === 0 ? "Show a hint" : "Show the next hint"}
          </button>
        )}
        {!solution && (
          <button className="button" type="button" onClick={() => setSolution(true)}>
            Show the solution
          </button>
        )}
      </div>
      {solution && (
        <div className="puzzle-solution">
          <h2>Solution</h2>
          <ol>
            {puzzle.solution.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
