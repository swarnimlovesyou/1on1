import type { Submission } from "./types";

/** What one browser run produced. */
export type PyRun = { stdout: string; stderr: string; ms: number; timedOut: boolean };

const LOAD_MS = 90_000; // first run downloads Pyodide (about 10 MB) before the clock starts
const RUN_MS = 10_000;

let worker: Worker | null = null;
let loaded = false;

function fresh() {
  worker?.terminate();
  worker = new Worker("/py-worker.js");
  loaded = false;
}

/** Runs Python in a Web Worker with stdin; a run over the time limit is stopped by discarding the worker. */
export function runPython(code: string, input: string): Promise<PyRun> {
  if (!worker) fresh();
  const w = worker!;
  return new Promise((resolve) => {
    let timer = loaded
      ? setTimeout(() => stop(true), RUN_MS)
      : setTimeout(() => stop(false, "Python took too long to load in this browser. Check the connection and retry."), LOAD_MS);
    const stop = (timedOut: boolean, stderr = "") => {
      clearTimeout(timer);
      fresh(); // the only way to interrupt running Python is to drop its worker
      resolve({ stdout: "", stderr, ms: timedOut ? RUN_MS : 0, timedOut });
    };
    w.onmessage = (e: MessageEvent<{ type: string } & Partial<PyRun>>) => {
      if (e.data.type === "ready") {
        loaded = true;
        clearTimeout(timer);
        timer = setTimeout(() => stop(true), RUN_MS);
        return;
      }
      clearTimeout(timer);
      loaded = true;
      resolve({ stdout: e.data.stdout ?? "", stderr: e.data.stderr ?? "", ms: e.data.ms ?? 0, timedOut: false });
    };
    w.onerror = (e) => stop(false, "Python could not start in this browser: " + (e.message || "worker error"));
    w.postMessage({ code, input });
  });
}

/** A browser run in the shape the result views already show. Never an official or graded result. */
export function toSubmission(run: PyRun, problem: string, code: string, input: string): Submission {
  const status = run.timedOut ? "TIME_LIMIT_EXCEEDED" : run.stderr.trim() ? "RUNTIME_ERROR" : "RAN_IN_BROWSER";
  return {
    id: "browser-" + crypto.randomUUID(),
    problem,
    code,
    language: "python",
    official: false,
    status,
    createdAt: new Date().toISOString(),
    message: run.timedOut
      ? `Stopped after ${RUN_MS / 1000} seconds. Ran in your browser; official grading uses the server.`
      : "Ran in your browser with Python (Pyodide). Not graded: official grading uses the server.",
    results: [
      {
        index: 0,
        status,
        public: true,
        input,
        actual: run.stdout,
        message: run.stderr.trim() || undefined,
        time: (run.ms / 1000).toFixed(3),
        memory: "",
      },
    ],
  };
}
