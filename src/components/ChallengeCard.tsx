import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle, ArrowRight, Lightbulb } from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { api } from "../api";
import { useApp } from "../context";
import type { AttemptResult, Challenge, Scene } from "../types";

export default function ChallengeCard({
  challenge,
  scene,
}: {
  challenge: Challenge;
  scene?: Scene;
}) {
  const { user, reload, progress } = useApp();
  const reduced = useReducedMotion();
  const [choice, setChoice] = useState<number>();
  const [fields, setFields] = useState<Record<string, string>>({});
  const [hint, setHint] = useState(false);
  // opening the hint before answering is review evidence: a hinted success repeats its interval
  const [hintSeen, setHintSeen] = useState(false);
  const mutation = useMutation({
    mutationFn: (answer: unknown) =>
      api<AttemptResult>(`/challenges/${challenge.id}/attempts`, {
        answer,
        requestId: crypto.randomUUID(),
        hintUsed: hintSeen,
      }),
    onSuccess: () => {
      if (user) reload();
    },
  });
  const passed = progress.attempts?.some(
    (attempt) => attempt.challengeId === challenge.id && attempt.correct,
  );
  const ready =
    challenge.kind === "manipulation"
      ? !!scene
      : challenge.kind === "dry-run"
        ? challenge.fields?.every((field) => fields[field.key]?.trim())
        : choice !== undefined;
  return (
    <section className="learning-challenge" aria-labelledby={challenge.id}>
      <div className="challenge-heading">
        <h3 id={challenge.id}>{challenge.title}</h3>
        {passed && (
          <span className="challenge-passed">
            <CheckCircle size={16} />
            Previously passed
          </span>
        )}
      </div>
      <p>{challenge.prompt}</p>
      {challenge.options && (
        <div
          className="checkpoint-options"
          role="group"
          aria-label={challenge.title}
        >
          {challenge.options.map((option, index) => (
            <button
              key={option}
              type="button"
              aria-pressed={choice === index}
              className={choice === index ? "selected" : ""}
              onClick={() => {
                setChoice(index);
                mutation.reset();
              }}
            >
              <span>{String.fromCharCode(65 + index)}</span>
              {option}
            </button>
          ))}
        </div>
      )}
      {challenge.kind === "dry-run" && (
        <>
          <p className="challenge-input-summary">
            Fixed input: <code>{challenge.scene?.input}</code>
            {challenge.scene?.algorithm === "tabulation" && (
              <> · n = {challenge.scene.target}</>
            )}
          </p>
          <div className="dry-run-fields">
            {challenge.fields?.map((field) => (
              <label key={field.key}>
                {field.label}
                <input
                  value={fields[field.key] ?? ""}
                  onChange={(event) => {
                    setFields({ ...fields, [field.key]: event.target.value });
                    mutation.reset();
                  }}
                  autoComplete="off"
                />
              </label>
            ))}
          </div>
        </>
      )}
      {challenge.kind === "manipulation" && (
        <p className="challenge-input-summary">
          Use the experiment above, select “Update experiment”, then check that
          input here. Current input:{" "}
          <code>{scene?.input ?? "No experiment available"}</code> · target / n
          / k: {scene?.target}
        </p>
      )}
      <div className="challenge-actions">
        <button
          className="button secondary small"
          disabled={!ready || mutation.isPending}
          onClick={() =>
            mutation.mutate(
              challenge.kind === "manipulation"
                ? scene
                : challenge.kind === "dry-run"
                  ? fields
                  : choice,
            )
          }
        >
          {mutation.isPending
            ? "Checking…"
            : challenge.kind === "dry-run"
              ? "Check my dry run"
              : challenge.kind === "manipulation"
                ? "Check this input"
                : "Check my intuition"}
          <ArrowRight size={16} />
        </button>
        <button
          className="hint-link"
          onClick={() => {
            setHint(!hint);
            setHintSeen(true);
          }}
          aria-expanded={hint}
        >
          <Lightbulb size={17} />
          {hint ? "Hide hint" : "A small hint"}
        </button>
      </div>
      {hint && <p className="challenge-hint">{challenge.hint}</p>}
      {mutation.error && (
        <p className="inline-alert" role="alert">
          {mutation.error.message}
        </p>
      )}
      {mutation.data && (
        <motion.div
          initial={false}
          animate={{ opacity: 1 }}
          transition={{ duration: reduced ? 0 : 0.18 }}
          className={
            "challenge-feedback " + (mutation.data.correct ? "is-correct" : "")
          }
          role="status"
        >
          {mutation.data.correct && <CheckCircle size={20} />}
          <div>
            <p>{mutation.data.feedback}</p>
            {mutation.data.explanation && <p>{mutation.data.explanation}</p>}
            {!mutation.data.saved && (
              <small>
                Sign in to keep this attempt in your learning record.
              </small>
            )}
          </div>
        </motion.div>
      )}
    </section>
  );
}
