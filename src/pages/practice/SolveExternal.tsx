import { lazy, Suspense, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowUpRight, Play } from "@phosphor-icons/react";
import { api } from "../../api";
import type { BankItem, Submission } from "../../types";
import CompanyTags from "../../components/CompanyTags";
import ReportAsked from "../../components/ReportAsked";
import { Loading, ErrorState } from "../../components/Shared";
import FamilyMark from "../../components/FamilyMark";
import { familyOfProblem } from "../../families";
import { starters } from "../Practice";

const CodeEditor = lazy(() => import("../../components/CodeEditor"));

const draftKey = (id: string, language: string) => `1on1-external-draft:${id}:${language}`;
function readDraft(id: string, language: string) {
  try {
    return localStorage.getItem(draftKey(id, language));
  } catch {
    return null;
  }
}
function writeDraft(id: string, language: string, code: string) {
  try {
    localStorage.setItem(draftKey(id, language), code);
  } catch {
    // private windows can block storage; the editor still works without saving
  }
}

/** An external question in our editor. The statement stays on its own site; runs use the learner's own input. */
export default function SolveExternal() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const item = useQuery({ queryKey: ["bank-item", id], queryFn: () => api<BankItem>("/bank/item/" + id) });
  const [language, setLanguage] = useState("python"),
    [code, setCode] = useState(""),
    [input, setInput] = useState(""),
    [job, setJob] = useState<string>();
  useEffect(() => {
    setCode(readDraft(id, language) ?? starters[language]);
  }, [id, language]);
  const edit = (value: string) => {
    setCode(value);
    writeDraft(id, language, value);
  };
  const run = useMutation({
    mutationFn: () =>
      api<Submission>("/submissions", { problem: id, official: false, language, code, input, requestId: crypto.randomUUID() }),
    onSuccess: (s) => setJob(s.id),
  });
  const result = useQuery({
    queryKey: ["submission", job],
    queryFn: () => api<Submission>("/submissions/" + job),
    enabled: !!job,
    // stop on an error (an expired session, say) rather than retrying every second unseen
    refetchInterval: (q) => (q.state.error ? false : ["QUEUED", "RUNNING"].includes(q.state.data?.status ?? "QUEUED") ? 1000 : false),
    retry: false,
  });
  if (item.isLoading) return <Loading />;
  if (item.error || !item.data) return <ErrorState error={item.error} />;
  const q = item.data;
  const row = result.data?.results?.[0];
  return (
    <div className="solve-external">
      <Link
        className="back-link"
        to="/practice?tab=bank"
        onClick={(e) => {
          // back to the bank exactly as it was (filters and page live in its URL), when we came from inside the app
          if ((window.history.state?.idx ?? 0) > 0) {
            e.preventDefault();
            navigate(-1);
          }
        }}
      >
        <ArrowLeft size={16} aria-hidden="true" />
        Back to the question bank
      </Link>
      <div className="problem-heading solve-heading">
        <div>
          <FamilyMark family={familyOfProblem(q.tags)} label />
          <h1 className="display">{q.title}</h1>
          <div className="problem-title-meta">
            <span>{q.source}</span>
            {q.difficulty && <span className={"difficulty " + q.difficulty.toLowerCase()}>{q.difficulty}</span>}
            {q.tags.slice(0, 4).map((t) => (
              <span key={t}>{t}</span>
            ))}
          </div>
          <CompanyTags companies={q.companies} limit={4} />
          <ReportAsked questionId={q.id} />
        </div>
      </div>
      <p className="solve-statement">
        <a href={q.url} target="_blank" rel="noopener noreferrer">
          Read the full statement on {q.source} <ArrowUpRight size={14} aria-hidden="true" />
        </a>
        <span className="muted">
          {" "}
          1on1 doesn't copy statements. Write your solution here and run it on your own input.
          {q.source === "LeetCode" &&
            " LeetCode problems give a function signature: write a main that reads your input, calls your function and prints the result."}
        </span>
      </p>
      <div className="solve-workspace">
        <div className="solve-editor">
          <select aria-label="Coding language" value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          <Suspense fallback={<textarea className="code-fallback" aria-label="Code editor loading" value={code} onChange={(e) => edit(e.target.value)} />}>
            <CodeEditor value={code} onChange={edit} language={language} />
          </Suspense>
        </div>
        <div className="solve-run">
          <label>
            Your input
            <textarea rows={6} value={input} onChange={(e) => setInput(e.target.value)} placeholder="Paste a sample input from the statement" />
          </label>
          <button className="button primary small" disabled={run.isPending || !code.trim()} onClick={() => run.mutate()}>
            <Play size={16} aria-hidden="true" /> Run
          </button>
          {(run.error ?? result.error) && (
            <p className="run-error" role="alert">
              {(run.error ?? result.error)!.message}
            </p>
          )}
          {result.data && (
            <div className="run-output">
              <strong role="status">{result.data.status.replaceAll("_", " ").toLowerCase()}</strong>
              {row?.actual !== undefined && <pre className="reference-code">{row.actual || "(no output)"}</pre>}
              {(row?.message || result.data.message) && <p className="muted">{row?.message ?? result.data.message}</p>}
            </div>
          )}
          <p className="muted">There's no verdict here: compare your output with the statement's examples.</p>
        </div>
      </div>
    </div>
  );
}
