import { useEffect, useRef, useState } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  ArrowCounterClockwise,
  ArrowRight,
  ArrowsOutSimple,
  Check,
} from "@phosphor-icons/react";
import { api } from "../api";
import type { Scene, Trace } from "../types";
import { ErrorState } from "./Shared";
import SceneCanvas from "./experiment/SceneCanvas";
import { usePlayback } from "./experiment/usePlayback";

type Props = {
  scene: Scene;
  code?: string[];
  compact?: boolean;
  onStep?: (scene: Scene, step: number) => void;
  initialStep?: number;
};
export default function Experiment({
  scene,
  code,
  compact = false,
  onStep,
  initialStep = 0,
}: Props) {
  const [input, setInput] = useState(scene.input),
    [target, setTarget] = useState(scene.target),
    [words, setWords] = useState(scene.words ?? "");
  const [trace, setTrace] = useState<Trace>(),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<Error>(),
    [expanded, setExpanded] = useState(false);
  const { state, dispatch } = usePlayback();
  const container = useRef<HTMLElement>(null),
    latest = useRef(0),
    callback = useRef(onStep),
    controller = useRef<AbortController | undefined>(undefined);
  callback.current = onStep;
  const sceneKey = JSON.stringify(scene);
  async function run(next: Scene, index = 0) {
    const revision = ++latest.current;
    controller.current?.abort();
    const abort = new AbortController();
    controller.current = abort;
    dispatch({ type: "pause" });
    setBusy(true);
    setError(undefined);
    try {
      const data = await api<Trace>("/experiments", next, "POST", abort.signal);
      if (revision !== latest.current) return;
      setTrace(data);
      dispatch({ type: "load", count: data.steps.length, index });
      setInput(data.input.input);
      setTarget(data.input.target);
      setWords(data.input.words ?? "");
    } catch (caught) {
      if (revision === latest.current && !abort.signal.aborted)
        setError(caught as Error);
    } finally {
      if (revision === latest.current) setBusy(false);
    }
  }
  useEffect(() => {
    void run(scene, initialStep);
    return () => {
      latest.current++;
      controller.current?.abort();
    };
  }, [sceneKey]);
  useEffect(() => {
    if (trace) callback.current?.(trace.input, state.index);
  }, [trace, state.index]);
  useEffect(() => {
    if (typeof IntersectionObserver === "undefined" || !container.current)
      return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries[0].isIntersecting) dispatch({ type: "pause" });
    });
    observer.observe(container.current);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const change = () =>
      setExpanded(document.fullscreenElement === container.current);
    document.addEventListener("fullscreenchange", change);
    return () => document.removeEventListener("fullscreenchange", change);
  }, []);
  const step = trace?.steps[state.index];
  const draft: Scene = {
    algorithm: scene.algorithm,
    input,
    target,
    words,
    seed: scene.seed ?? 42,
  };
  return (
    <section
      ref={container}
      tabIndex={0}
      className={
        "experiment " +
        (compact ? "compact " : "") +
        (expanded ? "expanded" : "")
      }
      aria-label="Interactive algorithm experiment"
      aria-busy={busy}
      onKeyDown={(event) => {
        if (
          (event.target as HTMLElement).closest(
            "input,textarea,select,button,a",
          )
        )
          return;
        if (event.key === "ArrowRight") {
          event.preventDefault();
          dispatch({ type: "step", by: 1 });
        }
        if (event.key === "ArrowLeft") {
          event.preventDefault();
          dispatch({ type: "step", by: -1 });
        }
        if (event.key === " ") {
          event.preventDefault();
          dispatch({ type: "toggle" });
        }
        if (event.key === "Home") {
          event.preventDefault();
          dispatch({ type: "seek", index: 0 });
        }
      }}
    >
      <div className="experiment-top">
        <span>Interactive experiment</span>
        <div>
          {!compact && (
            <span className="experiment-computed">
              <Check size={14} />
              Computed in Java
            </span>
          )}
          <button
            className="icon-btn"
            aria-label={
              expanded ? "Restore experiment size" : "Expand experiment"
            }
            onClick={() => {
              if (expanded) void document.exitFullscreen();
              else
                void container.current
                  ?.requestFullscreen()
                  .catch(() =>
                    setError(
                      new Error(
                        "Fullscreen is unavailable here. The inline experiment remains usable.",
                      ),
                    ),
                  );
            }}
          >
            <ArrowsOutSimple size={18} />
          </button>
        </div>
      </div>
      {error && <ErrorState error={error} retry={() => void run(draft)} />}
      {!compact && (
        <div className="experiment-meta">
          <strong>{scene.algorithm.replaceAll("-", " ")}</strong>
          <span>
            {scene.algorithm === "sliding-window"
              ? `Window size: ${trace?.input.target ?? target}`
              : scene.algorithm === "tabulation"
                ? `Building F(${trace?.input.target ?? target})`
                : "Change the input. Follow what changes."}
          </span>
        </div>
      )}
      <div className="experiment-visual">
        {step ? (
          <SceneCanvas
            step={step}
            family={trace!.family}
            duration={Math.min(0.55, state.speed / 2000)}
            instant={state.instant}
          />
        ) : (
          <div className="skeleton panel" />
        )}
      </div>
      {step && (
        <>
          <div className="variables">
            {Object.entries(step.variables).map(([key, value]) => (
              <span key={key}>
                <small>{key}</small>
                <strong>
                  {Array.isArray(value)
                    ? value.length
                      ? value.join(", ")
                      : "empty"
                    : String(value)}
                </strong>
              </span>
            ))}
          </div>
          <div
            className="step-explanation"
            aria-live={state.playing ? "off" : "polite"}
          >
            <span className="step-number">
              {String(state.index + 1).padStart(2, "0")}
            </span>
            <p>{step.text}</p>
          </div>
        </>
      )}
      {code && !compact && (
        <div
          className="trace-code"
          aria-label="Minimal implementation linked to execution"
        >
          {code.map((line, index) => (
            <div
              key={index}
              className={index === step?.line ? "current-line" : ""}
              aria-current={index === step?.line ? "step" : undefined}
            >
              <span>{index + 1}</span>
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
            disabled={!trace}
            onClick={() => dispatch({ type: "seek", index: 0 })}
          >
            <ArrowCounterClockwise size={18} />
          </button>
          <button
            className="icon-btn"
            aria-label="Previous step"
            disabled={!trace || state.index === 0}
            onClick={() => dispatch({ type: "step", by: -1 })}
          >
            <SkipBack size={18} />
          </button>
          <button
            className="play-button"
            aria-label={state.playing ? "Pause animation" : "Play animation"}
            disabled={!trace || busy}
            onClick={() => dispatch({ type: "toggle" })}
          >
            {state.playing ? (
              <Pause size={18} weight="fill" />
            ) : (
              <Play size={18} weight="fill" />
            )}
          </button>
          <button
            className="icon-btn"
            aria-label="Next step"
            disabled={!trace || state.index >= state.count - 1 || busy}
            onClick={() => dispatch({ type: "step", by: 1 })}
          >
            <SkipForward size={18} />
          </button>
        </div>
        <span className="step-count">
          {state.index + 1} <span>/ {state.count || "—"} steps</span>
        </span>
        {!compact && (
          <select
            aria-label="Playback speed"
            value={state.speed}
            onChange={(event) =>
              dispatch({ type: "speed", value: Number(event.target.value) })
            }
          >
            <option value={1500}>0.5×</option>
            <option value={900}>1×</option>
            <option value={450}>2×</option>
          </select>
        )}
      </div>
      {!compact && (
        <>
          <label className="trace-scrubber">
            Step through the execution
            <input
              type="range"
              aria-label="Execution step"
              min={0}
              max={Math.max(0, state.count - 1)}
              value={state.index}
              disabled={!trace || busy}
              onChange={(event) =>
                dispatch({ type: "seek", index: Number(event.target.value) })
              }
            />
          </label>
          <form
            className="experiment-inputs"
            onSubmit={(event) => {
              event.preventDefault();
              void run(draft);
            }}
          >
            {![
              "recursion",
              "memoization",
              "tabulation",
              "trie",
              "bloom-filter",
            ].includes(scene.algorithm) && (
              <label>
                Your input
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="2, 1, 5, 1, 3, 2"
                />
              </label>
            )}
            {[
              "binary-search",
              "two-pointers",
              "sliding-window",
              "recursion",
              "memoization",
              "tabulation",
              "quickselect",
            ].includes(scene.algorithm) && (
              <label className="target-input">
                {scene.algorithm === "sliding-window"
                  ? "Window size"
                  : scene.algorithm === "tabulation"
                    ? "n"
                    : "Target / n / k"}
                <input
                  type="number"
                  min={
                    ["binary-search", "two-pointers"].includes(scene.algorithm)
                      ? -10000
                      : 0
                  }
                  max={10000}
                  value={target}
                  onChange={(event) => setTarget(Number(event.target.value))}
                />
              </label>
            )}
            {["trie", "bloom-filter"].includes(scene.algorithm) && (
              <label>
                Words
                <input
                  value={words}
                  onChange={(event) => setWords(event.target.value)}
                />
              </label>
            )}
            <button className="button secondary small" disabled={busy}>
              Update experiment
              <ArrowRight size={16} />
            </button>
          </form>
          {["binary-search", "two-pointers"].includes(scene.algorithm) && (
            <p className="experiment-footnote">
              Input preparation sorts the values before the search phase.
            </p>
          )}
          {["bfs", "dfs", "dijkstra", "max-flow"].includes(scene.algorithm) && (
            <p className="experiment-footnote">
              A small directed graph is derived from your values. Numeric labels
              match the code; BFS ignores the edge weights.
            </p>
          )}
          <details className="trace-transcript">
            <summary>Read the execution as text</summary>
            <ol>
              {trace?.steps.map((item) => (
                <li key={item.id}>
                  {item.text} Values: {item.array.join(", ")}.
                </li>
              ))}
            </ol>
          </details>
        </>
      )}
    </section>
  );
}
