import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { Loading, ErrorState, PageHeading } from "../components/Shared";

type Measure = { algorithm: string; sizes: number[]; steps: number[]; curves: Record<string, number[]>; closest: string };

const ALGORITHMS = [
  ["binary-search", "Binary search"],
  ["two-pointers", "Two pointers"],
  ["sliding-window", "Sliding window"],
  ["merge-sort", "Merge sort"],
  ["quick-sort", "Quicksort"],
] as const;
// each reference curve gets its own dash so identity never depends on colour
const DASH: Record<string, string> = { "log n": "2 4", n: "8 4", "n log n": "1 0", "n²": "10 4 2 4" };

const W = 640, H = 300, L = 48, R = 16, T = 16, B = 36;

/** Phase 3 performance lab: how many trace steps an algorithm takes as its input grows. */
export default function LabPage() {
  const [algorithm, setAlgorithm] = useState<string>("merge-sort");
  const lab = useQuery({ queryKey: ["lab", algorithm], queryFn: () => api<Measure>("/lab/" + algorithm), staleTime: Infinity });
  return (
    <>
      <PageHeading
        title="Performance lab"
        description="Run an algorithm on random inputs of 4, 8, 16 and 32 values, count its steps, and see which growth curve it follows."
      />
      <div className="contest-filters" role="group" aria-label="Algorithm">
        {ALGORITHMS.map(([id, label]) => (
          <button key={id} type="button" className={algorithm === id ? "active" : ""} aria-pressed={algorithm === id} onClick={() => setAlgorithm(id)}>
            {label}
          </button>
        ))}
      </div>
      {lab.isLoading ? <Loading /> : lab.error || !lab.data ? <ErrorState error={lab.error} retry={() => lab.refetch()} /> : <Chart m={lab.data} />}
      <p className="muted lab-note">
        Counts are steps of the real Java trace, not time on a clock: each step is one comparison, move or update the animation shows.
        Inputs stop at 32 values, the teaching limit, so curves that only separate at large n can still look close. Each size is the
        average of three seeded random inputs; searches look for a value that is absent, so they do their full work.
      </p>
    </>
  );
}

function Chart({ m }: { m: Measure }) {
  const maxY = Math.max(...m.steps, ...Object.values(m.curves).flat()) * 1.08;
  const x = (n: number) => L + ((n - m.sizes[0]) / (m.sizes.at(-1)! - m.sizes[0])) * (W - L - R);
  const y = (v: number) => T + (1 - v / maxY) * (H - T - B);
  const path = (values: number[]) => values.map((v, i) => `${i ? "L" : "M"}${x(m.sizes[i]).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(f * maxY));
  return (
    <figure className="lab-figure">
      <p className="lab-verdict">
        Closest growth: <strong>{m.closest}</strong>
      </p>
      <div className="lab-legend" aria-hidden="true">
        <span>
          <i className="lab-swatch measured" /> Measured steps
        </span>
        <span>
          <i className="lab-swatch reference" /> Reference curves, scaled to meet the measurement at n = 32
        </span>
      </div>
      <svg className="lab-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Steps against input size; closest growth ${m.closest}`}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} className="lab-grid" />
            <text x={L - 8} y={y(t) + 4} textAnchor="end" className="lab-axis">
              {t}
            </text>
          </g>
        ))}
        {m.sizes.map((n) => (
          <text key={n} x={x(n)} y={H - 12} textAnchor="middle" className="lab-axis">
            n = {n}
          </text>
        ))}
        {Object.entries(m.curves).map(([name, values]) => (
          <g key={name}>
            <path d={path(values)} className={"lab-curve" + (name === m.closest ? " closest" : "")} strokeDasharray={DASH[name]} />
            <text x={x(m.sizes[2]) + 8} y={y(values[2]) + (name === "n log n" || name === "n²" ? 16 : -8)} className="lab-curve-label">
              {name}
            </text>
          </g>
        ))}
        <path d={path(m.steps)} className="lab-measured" />
        {m.steps.map((v, i) => (
          <g key={i} className="lab-point">
            <circle cx={x(m.sizes[i])} cy={y(v)} r={14} className="lab-hit">
              <title>{`n = ${m.sizes[i]}: ${v.toFixed(1)} steps`}</title>
            </circle>
            <circle cx={x(m.sizes[i])} cy={y(v)} r={5} className="lab-dot" />
          </g>
        ))}
      </svg>
      <table className="lab-table">
        <caption className="sr-only">Measured steps and reference curves by input size</caption>
        <thead>
          <tr>
            <th>Input size</th>
            <th>Measured steps</th>
            {Object.keys(m.curves).map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {m.sizes.map((n, i) => (
            <tr key={n}>
              <td>{n}</td>
              <td>{m.steps[i].toFixed(1)}</td>
              {Object.values(m.curves).map((c, j) => (
                <td key={j}>{c[i].toFixed(1)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
