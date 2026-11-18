import { useEffect, useMemo, useState } from "react";
import { Pause, Play } from "@phosphor-icons/react";

type Frame = {
  lo: number;
  hi: number;
  mid: number | null;
  found: boolean;
  text: string;
};

const VALUES = [3, 8, 12, 17, 23, 31, 42, 56];
const TARGET = 42;

/** Binary search for TARGET, one move per frame: the same idea every lesson animates, in miniature. */
export function frames(values: number[], target: number): Frame[] {
  const out: Frame[] = [
    {
      lo: 0,
      hi: values.length - 1,
      mid: null,
      found: false,
      text: `Find ${target}. The answer, if it's here, lies between lo and hi.`,
    },
  ];
  let lo = 0,
    hi = values.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (values[mid] === target) {
      out.push({
        lo,
        hi,
        mid,
        found: true,
        text: `values[${mid}] is ${target}. Found in ${out.length} moves, not ${values.length}.`,
      });
      return out;
    }
    const right = values[mid] < target;
    out.push({
      lo,
      hi,
      mid,
      found: false,
      text: `values[${mid}] = ${values[mid]} is ${right ? "smaller" : "larger"}, so drop the ${right ? "left" : "right"} half.`,
    });
    if (right) lo = mid + 1;
    else hi = mid - 1;
  }
  out.push({ lo, hi, mid: null, found: false, text: `${target} is not here.` });
  return out;
}

export default function HeroStepper() {
  const all = useMemo(() => frames(VALUES, TARGET), []);
  const reduced =
    typeof matchMedia === "function" &&
    matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [at, setAt] = useState(0);
  const [playing, setPlaying] = useState(!reduced);
  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setAt((i) => (i + 1) % (all.length + 1)), 1700); // one beat of rest on the answer
    return () => clearInterval(t);
  }, [playing, all.length]);
  const f = all[Math.min(at, all.length - 1)];
  return (
    <figure
      className="hero-stepper"
      aria-label={`Binary search for ${TARGET}, step by step`}
    >
      <div className="hero-stepper-top">
        <span>Binary search</span>
        <span className="hero-stepper-count">
          Step {Math.min(at, all.length - 1) + 1} of {all.length}
        </span>
        <button
          type="button"
          className="hero-stepper-toggle"
          onClick={() => setPlaying((p) => !p)}
          aria-label={playing ? "Pause the animation" : "Play the animation"}
        >
          {playing ? (
            <Pause size={14} weight="fill" />
          ) : (
            <Play size={14} weight="fill" />
          )}
        </button>
      </div>
      <ol className="hero-stepper-cells">
        {VALUES.map((v, i) => {
          const out = i < f.lo || i > f.hi;
          const state =
            f.mid === i ? (f.found ? "found" : "mid") : out ? "out" : "";
          return (
            <li key={v} className={state}>
              <span>{v}</span>
              <small>
                {i === f.lo && i === f.hi
                  ? "lo hi"
                  : i === f.lo
                    ? "lo"
                    : i === f.hi
                      ? "hi"
                      : i === f.mid
                        ? "mid"
                        : i}
              </small>
            </li>
          );
        })}
      </ol>
      <figcaption aria-live="polite">{f.text}</figcaption>
      <div
        className="hero-stepper-dots"
        role="group"
        aria-label="Choose a step"
      >
        {all.map((_, i) => (
          <button
            key={i}
            type="button"
            className={i === Math.min(at, all.length - 1) ? "current" : ""}
            aria-label={`Step ${i + 1}`}
            onClick={() => {
              setPlaying(false);
              setAt(i);
            }}
          />
        ))}
      </div>
    </figure>
  );
}
