import { motion } from "motion/react";
import type { Step } from "../../types";
import {
  Model,
  Label,
  CellStrip,
  Equation,
  list,
  numeric,
  type Timing,
} from "./LabPrimitives";

export default function AdvancedModel({
  step,
  algorithm,
  timing,
}: {
  step: Step;
  algorithm: string;
  timing: Timing;
}) {
  const v = step.visual ?? {};
  if (algorithm === "bloom-filter") {
    const hashes = list<number>(v.hashes);
    return (
      <Model
        title="Bits can rule out, not prove membership"
        subtitle="Two bounded hash positions share a 16-bit array. Collisions are intentional."
      >
        <div className="lab-hash-routes">
          <strong>{String(v.word ?? "word")}</strong>
          {hashes.map((hash, i) => (
            <div key={i}>
              <span>h{i + 1}(word)</span>
              <span>→ bit {hash}</span>
            </div>
          ))}
        </div>
        <CellStrip
          items={step.array.map((value, i) => ({
            id: "bit-" + i,
            label: value,
            index: i,
            state: hashes.includes(i)
              ? "active"
              : value === 1
                ? "resolved"
                : "",
          }))}
          timing={timing}
          label="Bloom filter bits"
        />
        {v.phase === "query" ? (
          <Equation>
            {v.possible ? "Possibly present" : "Definitely absent"} · exact
            check: {v.exact ? "present" : "absent"}
            {Boolean(v.possible) && !v.exact && " · false positive"}
          </Equation>
        ) : (
          <Label>
            Insertion only sets bits. It never clears a bit belonging to another
            word.
          </Label>
        )}
      </Model>
    );
  }
  const goals = list<string>(v.universe),
    sets = list<string[]>(v.sets),
    remaining = list<string>(v.remaining),
    selected = list<number>(v.selected),
    candidate = numeric(v.candidate),
    gain = list<string>(v.gain);
  return (
    <Model
      title="Cover the unmet goals"
      subtitle="Compare additional coverage, choose a candidate, then update the remaining universe."
      legend="This unit-cost greedy selection is approximate; it does not claim a minimum-size set."
    >
      <Label>Requested topics</Label>
      <div className="lab-coverage-goals">
        {goals.map((goal) => (
          <motion.span
            key={goal}
            className={remaining.includes(goal) ? "" : "resolved"}
            initial={false}
            animate={{ opacity: remaining.includes(goal) ? 1 : 0.7 }}
            transition={timing}
          >
            {goal}
            <small>{remaining.includes(goal) ? "uncovered" : "covered"}</small>
          </motion.span>
        ))}
      </div>
      <div
        className="lab-coverage-matrix"
        role="table"
        aria-label="Candidate coverage matrix"
      >
        <div
          className="lab-coverage-table"
          style={{
            gridTemplateColumns: `140px repeat(${Math.max(1, goals.length)},80px)`,
          }}
        >
          <span>candidate</span>
          {goals.map((g) => (
            <strong key={g}>{g}</strong>
          ))}
          {sets.map((set, i) => (
            <div
              className={
                "lab-coverage-row " +
                (i === candidate ? "active " : "") +
                (selected.includes(i) ? "selected" : "")
              }
              key={i}
              role="row"
            >
              <strong>
                Problem {i + 1}
                {selected.includes(i) ? " · chosen" : ""}
              </strong>
              {goals.map((goal) => (
                <span
                  key={goal}
                  className={set.includes(goal) ? "covered" : ""}
                >
                  {set.includes(goal) ? "yes" : "—"}
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>
      <Equation>
        {candidate >= 0
          ? `Candidate ${candidate + 1} · new coverage: ${gain.length ? gain.join(", ") : "none"}`
          : "Evaluate the first candidate."}
      </Equation>
      {!!selected.length && (
        <>
          <Label>Selected in order</Label>
          <CellStrip
            items={selected.map((i, position) => ({
              id: "chosen-" + i,
              label: `P${i + 1}`,
              index: position + 1,
              state: "resolved",
            }))}
            timing={timing}
            label="Chosen coverage candidates"
          />
        </>
      )}
    </Model>
  );
}
