import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  ArrowCounterClockwise,
  ArrowRight,
  ArrowsOutSimple,
  Check,
} from "@phosphor-icons/react";
import { api } from "../api";
import type { Scene, Step, Trace, Tree } from "../types";
import { ErrorState } from "./Shared";
export function StateView({ step, family }: { step: Step; family: string }) {
  if (family === "graph" && step.edges) {
    const n = step.vertexCount ?? 6,
      positions = Array.from({ length: n }, (_, i) => ({
        x: 70 + (i % 4) * 130,
        y: 60 + Math.floor(i / 4) * 135,
      }));
    return (
      <svg
        className="diagram"
        viewBox="0 0 560 270"
        role="img"
        aria-label="Directed graph; highlighted vertex is currently being processed"
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="24"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
        </defs>
        {step.edges.map((e, i) => (
          <g key={i}>
            <line
              className="graph-edge"
              x1={positions[e.from].x}
              y1={positions[e.from].y}
              x2={positions[e.to].x}
              y2={positions[e.to].y}
              markerEnd="url(#arrow)"
            />
            <text
              className="edge-label"
              x={(positions[e.from].x + positions[e.to].x) / 2}
              y={(positions[e.from].y + positions[e.to].y) / 2 - 10}
            >
              {e.weight}
            </text>
          </g>
        ))}
        {positions.map((p, i) => (
          <g key={i}>
            <circle
              className={
                "graph-node " + (step.active.includes(i) ? "active" : "")
              }
              cx={p.x}
              cy={p.y}
              r={23}
            />
            <text className="node-label" x={p.x} y={p.y + 5}>
              {String.fromCharCode(65 + i)}
            </text>
            {step.array[i] >= 0 && (
              <text className="edge-label" x={p.x} y={p.y + 43}>
                {step.array[i]}
              </text>
            )}
          </g>
        ))}
      </svg>
    );
  }
  if (family === "tree" && step.tree) return <TreeView root={step.tree} />;
  if (family === "heap") {
    const tree = (i: number): Tree | null =>
      i >= step.array.length
        ? null
        : {
            value: step.array[i],
            left: tree(i * 2 + 1),
            right: tree(i * 2 + 2),
          };
    return <TreeView root={tree(0)} />;
  }
  if (family === "trie" && step.words) {
    const root: {
      value: string;
      children: Record<string, any>;
      end?: boolean;
    } = { value: "∅", children: {} };
    step.words.forEach((word) => {
      let node = root;
      for (const char of word) {
        node.children[char] ??= { value: char, children: {} };
        node = node.children[char];
      }
      node.end = true;
    });
    const nodes: {
      x: number;
      y: number;
      value: string;
      end?: boolean;
      parent?: number;
    }[] = [];
    let leaves = 0;
    const walk = (node: any, depth: number, parent?: number) => {
      const idx = nodes.length;
      nodes.push({
        x: 0,
        y: 30 + depth * 43,
        value: node.value,
        end: node.end,
        parent,
      });
      const keys = Object.keys(node.children);
      if (!keys.length) nodes[idx].x = 45 + leaves++ * 65;
      else {
        keys.forEach((k) => walk(node.children[k], depth + 1, idx));
        nodes[idx].x =
          nodes.filter((n) => n.parent === idx).reduce((s, n) => s + n.x, 0) /
          keys.length;
      }
    };
    walk(root, 0);
    return (
      <svg
        className="diagram trie-diagram"
        viewBox={`0 0 ${Math.max(420, leaves * 65 + 50)} 300`}
        role="img"
        aria-label="Trie with shared prefixes and filled word-ending nodes"
      >
        {nodes
          .filter((n) => n.parent !== undefined)
          .map((n, i) => (
            <line
              key={i}
              className="graph-edge"
              x1={n.x}
              y1={n.y}
              x2={nodes[n.parent!].x}
              y2={nodes[n.parent!].y}
            />
          ))}
        {nodes.map((n, i) => (
          <g key={i}>
            <circle
              className={"graph-node " + (n.end ? "active" : "")}
              cx={n.x}
              cy={n.y}
              r={16}
            />
            <text className="node-label" x={n.x} y={n.y + 5}>
              {n.value}
            </text>
          </g>
        ))}
      </svg>
    );
  }
  return (
    <div
      className={
        "array-stage " +
        (family === "stack" || family === "recursion" ? "stack-stage" : "")
      }
    >
      <div className={"array-values " + (family === "dp" ? "dp-values" : "")}>
        {step.array.length ? (
          step.array.map((value, i) => (
            <div className="array-item" key={i}>
              <span
                className={
                  "array-cell " + (step.active.includes(i) ? "active" : "")
                }
              >
                {value}
              </span>
              <span className="array-index">
                {family === "dp" ? `F(${i})` : i}
              </span>
              {family === "linked" && i < step.array.length - 1 && (
                <ArrowRight className="link-arrow" size={18} />
              )}
            </div>
          ))
        ) : (
          <span className="muted">The structure is empty.</span>
        )}
      </div>
      {family === "coverage" && step.topics && (
        <div className="coverage-topics">
          {step.topics.map((t) => (
            <span className="chip" key={t}>
              {t}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
function TreeView({ root }: { root: Tree | null }) {
  const nodes: { x: number; y: number; value: number; parent?: number }[] = [];
  function walk(
    n: Tree | null,
    x: number,
    y: number,
    span: number,
    parent?: number,
  ) {
    if (!n) return;
    const idx = nodes.length;
    nodes.push({ x, y, value: n.value, parent });
    walk(n.left, x - span, y + 64, span / 2, idx);
    walk(n.right, x + span, y + 64, span / 2, idx);
  }
  walk(root, 280, 35, 120);
  return (
    <svg
      className="diagram"
      viewBox={`0 0 560 ${Math.max(250, ...nodes.map((n) => n.y + 35))}`}
      role="img"
      aria-label="Tree after the current insertion"
    >
      {nodes
        .filter((n) => n.parent !== undefined)
        .map((n, i) => (
          <line
            className="graph-edge"
            key={i}
            x1={n.x}
            y1={n.y}
            x2={nodes[n.parent!].x}
            y2={nodes[n.parent!].y}
          />
        ))}
      {nodes.map((n, i) => (
        <g key={i}>
          <circle className="graph-node" cx={n.x} cy={n.y} r={21} />
          <text className="node-label" x={n.x} y={n.y + 5}>
            {n.value}
          </text>
        </g>
      ))}
    </svg>
  );
}
export default function Experiment({
  scene,
  code,
  compact = false,
  onStep,
  initialStep = 0,
}: {
  scene: Scene;
  code?: string[];
  compact?: boolean;
  onStep?: (scene: Scene, step: number) => void;
  initialStep?: number;
}) {
  const [input, setInput] = useState(scene.input),
    [target, setTarget] = useState(scene.target),
    [words, setWords] = useState(scene.words ?? ""),
    [trace, setTrace] = useState<Trace>(),
    [index, setIndex] = useState(0),
    [playing, setPlaying] = useState(false),
    [speed, setSpeed] = useState(900),
    [expanded, setExpanded] = useState(false);
  const run = useMutation({
    mutationFn: (s: Scene) => api<Trace>("/experiments", s),
    onSuccess: (data) => {
      setTrace(data);
      setIndex(Math.min(initialStep, data.steps.length - 1));
      setPlaying(false);
    },
  });
  const sceneKey = JSON.stringify(scene);
  useEffect(() => {
    setInput(scene.input);
    setTarget(scene.target);
    setWords(scene.words ?? "");
    run.mutate(scene);
  }, [sceneKey]);
  const count = trace?.steps.length ?? 0;
  const step = trace?.steps[index];
  useEffect(() => {
    if (!playing) return;
    const id = setInterval(
      () =>
        setIndex((i) => {
          if (i >= count - 1) {
            setPlaying(false);
            return i;
          }
          return i + 1;
        }),
      speed,
    );
    return () => clearInterval(id);
  }, [playing, count, speed]);
  useEffect(() => {
    if (trace) onStep?.(trace.input, index);
  }, [trace, index]);
  const ref = useRef<HTMLDivElement>(null);
  return (
    <section
      ref={ref}
      className={
        "experiment " +
        (compact ? "compact " : "") +
        (expanded ? "expanded" : "")
      }
      aria-label="Interactive algorithm experiment"
    >
      <div className="experiment-top">
        <span>
          <span className="live-dot" />
          Interactive experiment
        </span>
        <div>
          {!compact && (
            <span className="experiment-computed">
              <Check size={13} />
              Computed in Java
            </span>
          )}
          <button
            className="icon-btn"
            aria-label={
              expanded ? "Restore experiment size" : "Expand experiment"
            }
            onClick={() => setExpanded(!expanded)}
          >
            <ArrowsOutSimple size={17} />
          </button>
        </div>
      </div>
      {run.isError ? (
        <ErrorState
          error={run.error}
          retry={() =>
            run.mutate({ algorithm: scene.algorithm, input, target, words })
          }
        />
      ) : (
        <>
          {!compact && (
            <div className="experiment-meta">
              <strong>{scene.algorithm.replaceAll("-", " ")}</strong>
              <span>
                {scene.algorithm === "sliding-window"
                  ? `Window size: ${target}`
                  : scene.algorithm === "binary-search"
                    ? `Target: ${target}`
                    : "Change the input. Watch the idea unfold."}
              </span>
            </div>
          )}
          <div className="experiment-visual">
            {step ? (
              <StateView step={step} family={trace!.family} />
            ) : (
              <div className="skeleton panel" />
            )}
          </div>
          {step && (
            <>
              <div className="variables">
                {Object.entries(step.variables).map(([k, v]) => (
                  <span key={k}>
                    <small>{k}</small>
                    <strong>
                      {Array.isArray(v) ? v.join(", ") : String(v)}
                    </strong>
                  </span>
                ))}
              </div>
              <div className="step-explanation" aria-live="polite">
                <span className="step-number">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <p>{step.text}</p>
              </div>
            </>
          )}
          {code && !compact && (
            <div className="trace-code">
              {code.map((line, i) => (
                <div key={i} className={i === step?.line ? "current-line" : ""}>
                  <span>{i + 1}</span>
                  <code>{line}</code>
                </div>
              ))}
            </div>
          )}
          <div className="playback">
            <div className="playback-buttons">
              <button
                className="icon-btn"
                aria-label="Reset experiment"
                onClick={() => {
                  setIndex(0);
                  setPlaying(false);
                }}
              >
                <ArrowCounterClockwise size={18} />
              </button>
              <button
                className="icon-btn"
                aria-label="Previous step"
                disabled={index === 0}
                onClick={() => {
                  setPlaying(false);
                  setIndex((i) => i - 1);
                }}
              >
                <SkipBack size={18} />
              </button>
              <button
                className="play-button"
                aria-label={playing ? "Pause animation" : "Play animation"}
                disabled={!trace}
                onClick={() => {
                  if (index >= count - 1) setIndex(0);
                  setPlaying(!playing);
                }}
              >
                {playing ? (
                  <Pause size={18} weight="fill" />
                ) : (
                  <Play size={18} weight="fill" />
                )}
              </button>
              <button
                className="icon-btn"
                aria-label="Next step"
                disabled={index >= count - 1}
                onClick={() => {
                  setPlaying(false);
                  setIndex((i) => i + 1);
                }}
              >
                <SkipForward size={18} />
              </button>
            </div>
            <span className="step-count">
              {index + 1} <span>/ {count || "—"} steps</span>
            </span>
            {!compact && (
              <select
                aria-label="Playback speed"
                value={speed}
                onChange={(e) => setSpeed(+e.target.value)}
              >
                <option value={1500}>0.5×</option>
                <option value={900}>1×</option>
                <option value={450}>2×</option>
              </select>
            )}
          </div>
          {!compact && (
            <>
              <form
                className="experiment-inputs"
                onSubmit={(e) => {
                  e.preventDefault();
                  run.mutate({
                    algorithm: scene.algorithm,
                    input,
                    target,
                    words,
                  });
                }}
              >
                <label>
                  Your input
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="2, 1, 5, 1, 3, 2"
                  />
                </label>
                <label className="target-input">
                  {scene.algorithm === "sliding-window"
                    ? "Window size"
                    : "Target / n / k"}
                  <input
                    type="number"
                    min={
                      ["two-pointers", "binary-search"].includes(
                        scene.algorithm,
                      )
                        ? -10000
                        : 0
                    }
                    max="10000"
                    value={target}
                    onChange={(e) => setTarget(+e.target.value)}
                  />
                </label>
                {["trie", "bloom-filter"].includes(scene.algorithm) && (
                  <label>
                    Words
                    <input
                      value={words}
                      onChange={(e) => setWords(e.target.value)}
                    />
                  </label>
                )}
                <button
                  className="button secondary small"
                  disabled={run.isPending}
                >
                  Update experiment <ArrowRight size={15} />
                </button>
              </form>
              {["two-pointers", "binary-search"].includes(scene.algorithm) && (
                <p className="experiment-footnote">
                  This experiment sorts your input before running the search.
                </p>
              )}
              {["bfs", "dfs", "dijkstra", "max-flow"].includes(
                scene.algorithm,
              ) && (
                <p className="experiment-footnote">
                  A directed graph is derived from your values. Labels show edge
                  weights or capacities.
                </p>
              )}
              <details className="trace-transcript">
                <summary>Read the execution as text</summary>
                <ol>
                  {trace?.steps.map((s) => (
                    <li key={s.id}>
                      {s.text} Values: {s.array.join(", ")}.
                    </li>
                  ))}
                </ol>
              </details>
            </>
          )}
        </>
      )}
    </section>
  );
}
