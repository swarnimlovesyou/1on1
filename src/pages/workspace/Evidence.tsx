import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Plus,
  Check,
  CheckCircle,
  Trash,
  BookmarkSimple,
  Notebook,
  CalendarBlank,
  ChartBar,
  Users,
  Plugs,
  ArrowClockwise,
  Download,
  Flask,
  ShieldCheck,
  ArrowLeft,
  Code,
  Lightbulb,
} from "@phosphor-icons/react";
import { api, download, resetCsrf } from "../../api";
import { useApp } from "../../context";
import type { Note, Plan, User } from "../../types";
import { useLessons, useProblems } from "../Learning";
import {
  Loading,
  ErrorState,
  PageHeading,
  Gate,
} from "../../components/Shared";
import Experiment from "../../components/Experiment";
export function Evidence() {
  return (
    <Gate>
      <EvidenceContent />
    </Gate>
  );
}
function EvidenceContent() {
  const [method, setMethod] = useState("quickselect");
  const q = useMutation({
    mutationFn: () => api<Record<string, any>>("/evidence", { method }),
  });
  const descriptions: Record<string, string> = {
    quickselect:
      "Randomized Quickselect finds an order statistic with expected O(n) time, worst O(n²). The baseline sorts a defensive copy, O(n log n). Both report the same order statistic.",
    trie: "The Java trie indexes title/topic prefixes. Queries follow prefix characters and enumerate bounded results. The linear baseline scans titles; index construction is excluded from query timings.",
    "set-cover":
      "Greedy set cover maximizes newly covered topics at each choice. The first-useful baseline accepts candidates in their input order. Compare selected question counts as well as time; greedy is not necessarily faster.",
  };
  return (
    <>
      <PageHeading
        title="Good ideas deserve evidence."
        description="Inspect the algorithms that make search, practice planning, and cohort summaries work."
      />
      <div className="evidence-methods">
        {[
          ["trie", "Prefix search", "Unit 4"],
          ["set-cover", "Practice coverage", "Unit 5"],
          ["quickselect", "Cohort quartiles", "Unit 6 · CO5"],
        ].map(([m, title, unit]) => (
          <button
            key={m}
            className={method === m ? "selected" : ""}
            onClick={() => {
              setMethod(m);
              q.reset();
            }}
          >
            <Flask size={22} />
            <strong>{title}</strong>
            <span>{unit}</span>
          </button>
        ))}
      </div>
      <section className="evidence-run">
        <h2>
          {method === "trie"
            ? "Follow a prefix. Find a concept."
            : method === "set-cover"
              ? "Cover the topics that matter."
              : "Find a threshold without sorting everything."}
        </h2>
        <p>{descriptions[method]}</p>
        <div className="evidence-config">
          <span>
            Seed <code>42</code>
          </span>
          <span>
            Warm-up <code>2 runs</code>
          </span>
          <span>
            Measured <code>5 runs</code>
          </span>
          <span>
            Sizes{" "}
            <code>
              {method === "set-cover" ? "100 · 1k · 10k" : "1k · 10k · 100k"}
            </code>
          </span>
        </div>
        <button
          className="button primary"
          onClick={() => q.mutate()}
          disabled={q.isPending}
        >
          {q.isPending
            ? "Running the experiment…"
            : "Run a reproducible benchmark"}
          <ArrowRight size={17} />
        </button>
        {q.error && <ErrorState error={q.error} />}
      </section>
      {q.data && (
        <section className="benchmark-results">
          <div className="section-heading">
            <h2>What happened on this machine</h2>
            <button
              className="button secondary small"
              onClick={() =>
                download("1on1-" + method + "-benchmark.json", q.data)
              }
            >
              <Download size={16} />
              Export evidence
            </button>
          </div>
          <table className="simple-table">
            <thead>
              <tr>
                <th>Input size</th>
                <th>Algorithm (ms)</th>
                <th>Baseline (ms)</th>
                {method === "set-cover" && (
                  <>
                    <th>Selected</th>
                    <th>Baseline selected</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {q.data.rows.map((r: any) => (
                <tr key={r.size}>
                  <td>{r.size.toLocaleString()}</td>
                  <td>{r.algorithmMs.toFixed(4)}</td>
                  <td>{r.baselineMs.toFixed(4)}</td>
                  {method === "set-cover" && (
                    <>
                      <td>{r.selected}</td>
                      <td>{r.baselineSelected}</td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="benchmark-chart">
            {q.data.rows.map((r: any) => {
              const max = Math.max(
                ...q.data!.rows.flatMap((x: any) => [
                  x.algorithmMs,
                  x.baselineMs,
                ]),
                0.00001,
              );
              return (
                <div className="benchmark-pair" key={r.size}>
                  <span>{r.size.toLocaleString()}</span>
                  <div>
                    <i
                      style={{
                        width: Math.max(1, (r.algorithmMs / max) * 100) + "%",
                      }}
                    />
                    <i
                      className="baseline"
                      style={{
                        width: Math.max(1, (r.baselineMs / max) * 100) + "%",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
          <p className="chart-legend">
            <span className="blue-dot" />
            Algorithm <span className="gray-dot" />
            Baseline
          </p>
          <p className="form-note">
            Java {q.data.java} · {q.data.os} · {q.data.processors} processors.{" "}
            {q.data.note}
          </p>
        </section>
      )}
    </>
  );
}
