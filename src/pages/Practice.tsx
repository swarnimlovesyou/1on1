import QuestionBank from "./practice/QuestionBank";
import Companies from "./practice/Companies";
import MockOA from "./practice/MockOA";
import Sheets from "./practice/Sheets";
import { clock, useCountdown, useIntegritySignals } from "./practice/mockTime";
import type { MockView } from "../types";
import FamilyMark from "../components/FamilyMark";
import { familyOfProblem, familyStyle } from "../families";
import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  MagnifyingGlass,
  ArrowUpRight,
  ArrowLeft,
  Play,
  PaperPlaneTilt,
  FloppyDisk,
  CheckCircle,
  Code,
  Lightbulb,
  Clock,
  ArrowRight,
  TerminalWindow,
} from "@phosphor-icons/react";
import { api } from "../api";
import type { Problem, Submission } from "../types";
import { useApp } from "../context";
import { useProblems } from "./Learning";
import {
  Loading,
  ErrorState,
  PageHeading,
  Bookmark,
} from "../components/Shared";
import Tutor from "../components/Tutor";
import CoachPanel from "../components/CoachPanel";
const CodeEditor = lazy(() => import("../components/CodeEditor"));
export const starters: Record<string, string> = {
  java: "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner input = new Scanner(System.in);\n        // Read the problem input and write your solution here.\n    }\n}\n",
  python:
    'import sys\n\ndef solve():\n    data = sys.stdin.read().strip()\n    # Read the problem input and write your solution here.\n\nif __name__ == "__main__":\n    solve()\n',
  cpp: "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Read the problem input and write your solution here.\n    return 0;\n}\n",
};
const PRACTICE_TABS: [string, string][] = [
  ["problems", "Problems"],
  ["bank", "Question bank"],
  ["sheets", "Sheets"],
  ["companies", "Companies"],
  ["mock", "Mock OA"],
];
export function Practice() {
  const [params, setParams] = useSearchParams();
  const tab = params.get("tab") ?? "problems";
  const q = useProblems(),
    { progress } = useApp(),
    [search, setSearch] = useState(""),
    [difficulty, setDifficulty] = useState("All"),
    topic = params.get("topic") ?? "All topics",
    setTopic = (t: string) => {
      const next = new URLSearchParams(window.location.search);
      if (t === "All topics") next.delete("topic");
      else next.set("topic", t);
      setParams(next, { replace: true });
    },
    [status, setStatus] = useState("All problems");
  if (q.isLoading) return <Loading />;
  if (q.error) return <ErrorState error={q.error} />;
  // every topic is visible at once, most common first, with how many problems it has
  const topicCounts = new Map<string, number>();
  for (const p of q.data ?? []) for (const t of p.topics) topicCounts.set(t, (topicCounts.get(t) ?? 0) + 1);
  const topics = ["All topics", ...[...topicCounts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([t]) => t)];
  const rows = q.data?.filter(
    (p) =>
      p.title.toLowerCase().includes(search.toLowerCase()) &&
      (difficulty === "All" || p.difficulty === difficulty) &&
      (topic === "All topics" || p.topics.includes(topic)) &&
      (status === "All problems" ||
        (status === "Solved"
          ? progress.solved.includes(p.id)
          : !progress.solved.includes(p.id))),
  );
  return (
    <>
      <PageHeading
        title="Turn an idea into instinct."
        description="A little thinking, a little debugging, and one more thing you can do."
        action={
          <span className="collection-count">
            <CheckCircle size={18} />
            {progress.solved.length} / 60 solved
          </span>
        }
      />
      <div className="tabs practice-tabs" role="tablist">
        {PRACTICE_TABS.map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={tab === key ? "active" : ""}
            onClick={() => setParams(key === "problems" ? {} : { tab: key })}
          >
            {label}
          </button>
        ))}
      </div>
      {tab === "sheets" ? (
        <Sheets />
      ) : tab === "bank" ? (
        <QuestionBank />
      ) : tab === "companies" ? (
        <Companies />
      ) : tab === "mock" ? (
        <MockOA />
      ) : (
        <>
      <div className="practice-banner">
        <span className="practice-icon">
          <Code size={29} />
        </span>
        <div>
          <h2>Practice with a purpose.</h2>
          <p>
            Build a set of questions around the topics you want to understand.
          </p>
        </div>
        <Link className="button secondary small" to="/plan">
          Build my plan <ArrowRight size={16} />
        </Link>
      </div>
      <div className="topic-chips" role="group" aria-label="Problem topic">
        {topics.map((t) => (
          <button key={t} type="button" className={topic === t ? "active" : ""} aria-pressed={topic === t} onClick={() => setTopic(t)}>
            {t}
            <span>{t === "All topics" ? q.data?.length ?? 0 : topicCounts.get(t)}</span>
          </button>
        ))}
      </div>
      <div className="practice-filters">
        <div className="search-field">
          <MagnifyingGlass size={17} />
          <input
            aria-label="Search practice problems"
            placeholder="Find a problem…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          aria-label="Difficulty"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
        >
          {["All", "Easy", "Medium", "Hard"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select
          aria-label="Completion status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          {["All problems", "Solved", "To explore"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </div>
      <div className="table-scroll">
        <table className="problem-table">
          <thead>
            <tr>
              <th>
                <span className="sr-only">Status</span>
              </th>
              <th>Problem</th>
              <th>Topics</th>
              <th>Difficulty</th>
              <th>
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {rows?.map((p) => (
              <tr key={p.id}>
                <td>
                  {progress.solved.includes(p.id) ? (
                    <CheckCircle className="success" size={20} weight="fill" />
                  ) : (
                    <span className="unsolved-dot" />
                  )}
                </td>
                <td>
                  <FamilyMark family={familyOfProblem(p.topics)} />
                  <Link to={"/practice/" + p.id}>{p.title}</Link>
                  <small className="problem-index">
                    {String(p.order).padStart(2, "0")}
                  </small>
                </td>
                <td>
                  <div className="table-tags">
                    {p.topics.slice(0, 2).map((t) => (
                      <span key={t}>{t}</span>
                    ))}
                  </div>
                </td>
                <td>
                  <span className={"difficulty " + p.difficulty.toLowerCase()}>
                    {p.difficulty}
                  </span>
                </td>
                <td>
                  <Bookmark id={p.id} />
                  <Link
                    to={"/practice/" + p.id}
                    className="icon-btn"
                    aria-label={"Solve " + p.title}
                  >
                    <ArrowUpRight size={18} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!rows?.length && (
        <div className="empty">
          <h2>No matching problems.</h2>
          <p>Change your filters to find another way in.</p>
        </div>
      )}
        </>
      )}
    </>
  );
}
function MockBanner({ id }: { id: string }) {
  const mock = useQuery({ queryKey: ["mock", id], queryFn: () => api<MockView>("/mocks/" + id), refetchInterval: 30000 });
  const remaining = useCountdown(mock.data?.remainingSeconds, mock.dataUpdatedAt);
  // learners solve here, so the integrity signals are recorded here too
  useIntegritySignals(mock.data && !mock.data.finished ? id : undefined, (kind) => {
    api(`/mocks/${id}/signals`, { kind }).catch(() => {});
  });
  if (!mock.data) return null;
  return (
    // a ticking timer is not announced; only the change to "ended" is
    <div className="mock-banner" role={mock.data.finished ? "status" : "timer"}>
      {mock.data.finished ? "This mock has ended; new runs no longer count." : `Mock in progress: ${clock(remaining)} left.`}
      <Link to="/practice?tab=mock">Back to the mock</Link>
    </div>
  );
}
export function ProblemPage() {
  const [searchParams] = useSearchParams();
  const mockId = searchParams.get("mock");
  const { id } = useParams(),
    { user, progress, progressReady, reload, notify } = useApp();
  const query = useQuery({
    queryKey: ["problem", id],
    queryFn: () => api<Problem>("/problems/" + id),
  });
  const [language, setLanguage] = useState("java"),
    [code, setCode] = useState(starters.java),
    [input, setInput] = useState(""),
    [tab, setTab] = useState("Description"),
    [hint, setHint] = useState(0),
    [job, setJob] = useState<string>(),
    [resultTab, setResultTab] = useState("Test results"),
    [saved, setSaved] = useState("");
  const localDrafts = useRef(new Map<string, string>());
  const draftKey = `${user?.id ?? "guest"}:${id}:${language}`;
  const editCode = (value: string) => {
    localDrafts.current.set(draftKey, value);
    setCode(value);
    setSaved("Unsaved changes");
  };
  useEffect(() => {
    if (!progressReady) return;
    const d = progress.drafts.find(
      (d) => d.problem === id && d.language === language,
    );
    setCode(localDrafts.current.get(draftKey) ?? d?.code ?? starters[language]);
    setSaved("");
    setJob(undefined);
  }, [id, language, progressReady, user?.id]);
  useEffect(() => {
    if (!user || !progressReady || saved !== "Unsaved changes") return;
    const timer = setTimeout(
      () =>
        api("/drafts/" + id, { language, code }, "PUT")
          .then(() => setSaved("Saved automatically"))
          .catch(() => setSaved("Save failed — retry")),
      1000,
    );
    return () => clearTimeout(timer);
  }, [id, language, code, saved, user?.id, progressReady]);
  const editorial = useQuery({
    queryKey: ["editorial", id],
    queryFn: () =>
      api<{
        editorial: string;
        reference: string;
        references?: Record<string, string>;
      }>("/problems/" + id + "/editorial"),
    enabled: tab === "Editorial",
  });
  const submission = useQuery({
    queryKey: ["submission", job],
    queryFn: () => api<Submission>("/submissions/" + job),
    enabled: !!job,
    refetchInterval: (q) =>
      ["QUEUED", "RUNNING"].includes(q.state.data?.status ?? "QUEUED")
        ? 1000
        : false,
  });
  useEffect(() => {
    if (
      submission.data &&
      !["QUEUED", "RUNNING"].includes(submission.data.status)
    )
      reload();
  }, [submission.data?.status]);
  const run = useMutation({
    mutationFn: (official: boolean) =>
      api<Submission>("/submissions", {
        problem: id,
        requestId: crypto.randomUUID(),
        language,
        code,
        input: input || query.data?.samples[0]?.input || "",
        official,
      }),
    onSuccess: (j) => {
      setJob(j.id);
      setResultTab("Test results");
    },
    onError: (e) => notify(e.message),
  });
  const save = async () => {
    try {
      await api("/drafts/" + id, { language, code }, "PUT");
      setSaved("Saved just now");
      reload();
    } catch (e) {
      notify((e as Error).message);
    }
  };
  if (query.isLoading) return <Loading />;
  if (query.error || !query.data) return <ErrorState error={query.error} />;
  const p = query.data,
    busy =
      run.isPending ||
      ["QUEUED", "RUNNING"].includes(submission.data?.status ?? "");
  return (
    <>
      {mockId && <MockBanner id={mockId} />}
      <Link className="back-link" to="/practice">
        <ArrowLeft size={16} />
        Back to practice
      </Link>
      <div className="problem-heading has-family" style={familyStyle(familyOfProblem(p.topics))}>
        <div>
          <FamilyMark family={familyOfProblem(p.topics)} label />
          <h1 className="display">{p.title}</h1>
          <div className="problem-title-meta">
            <span className={"difficulty " + p.difficulty.toLowerCase()}>
              {p.difficulty}
            </span>
            {p.topics.map((t) => (
              <span key={t}>{t}</span>
            ))}
            {progress.solved.includes(p.id) && (
              <span className="success">
                <CheckCircle size={16} />
                Solved
              </span>
            )}
          </div>
        </div>
        <div>
          <Bookmark id={p.id} />
          <Tutor
            problem={id}
            language={language}
            code={code}
            submission={job}
          />
        </div>
      </div>
      <div className="coding-workspace has-family" style={familyStyle(familyOfProblem(p.topics))}>
        <section className="problem-statement">
          <div className="tabs">
            {["Description", "Hints", "Coach", "Editorial"].map((t) => (
              <button
                key={t}
                className={tab === t ? "active" : ""}
                onClick={() => setTab(t)}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="statement-body">
            {tab === "Description" ? (
              <>
                <p className="prose">{p.description}</p>
                <h3>Input</h3>
                <p>{p.inputFormat}</p>
                <h3>Output</h3>
                <p>{p.outputFormat}</p>
                <h3>Try these examples</h3>
                {p.samples.map((s, i) => (
                  <div className="sample" key={i}>
                    <span>Example {i + 1}</span>
                    <div>
                      <small>Input</small>
                      <pre>{s.input}</pre>
                    </div>
                    <div>
                      <small>Output</small>
                      <pre>{s.output}</pre>
                    </div>
                  </div>
                ))}
                <h3>Constraints</h3>
                <p>{p.constraints}</p>
                <div className="statement-note">
                  <Lightbulb size={18} />
                  <p>
                    Use stdin and stdout. There’s no hidden function signature
                    to guess.
                  </p>
                </div>
              </>
            ) : tab === "Hints" ? (
              <>
                <h3>A nudge in the right direction.</h3>
                <p>
                  Take one hint at a time. Leave yourself room to discover the
                  next step.
                </p>
                {p.hints.slice(0, hint).map((h, i) => (
                  <div className="hint" key={h}>
                    <span>{i + 1}</span>
                    {h}
                  </div>
                ))}
                <button
                  className="button secondary small"
                  disabled={hint >= p.hints.length}
                  onClick={() => setHint((h) => h + 1)}
                >
                  {hint >= p.hints.length
                    ? "All hints revealed"
                    : "Reveal the next hint"}
                  <Lightbulb size={16} />
                </button>
              </>
            ) : tab === "Coach" ? (
              <CoachPanel
                problem={id!}
                language={language}
                refreshKey={`${saved}:${submission.data?.status ?? ""}`}
              />
            ) : editorial.isLoading ? (
              <Loading />
            ) : editorial.error ? (
              <ErrorState error={editorial.error} />
            ) : (
              <>
                <h3>One way to reason about it</h3>
                <p className="preserve-lines prose">{editorial.data?.editorial}</p>
                <h3>
                  {(editorial.data?.references?.[language]
                    ? language
                    : "java") === "cpp"
                    ? "C++"
                    : (editorial.data?.references?.[language]
                          ? language
                          : "java") === "python"
                      ? "Python"
                      : "Java"}{" "}
                  reference solution
                </h3>
                {language !== "java" &&
                  !editorial.data?.references?.[language] && (
                    <p className="muted">
                      There is no {language === "cpp" ? "C++" : "Python"}{" "}
                      reference for this problem yet, so the Java one is shown.
                      You can still submit your own{" "}
                      {language === "cpp" ? "C++" : "Python"} solution.
                    </p>
                  )}
                <pre className="reference-code">
                  {editorial.data?.references?.[language] ??
                    editorial.data?.reference}
                </pre>
              </>
            )}
          </div>
        </section>
        <section className="editor-panel">
          <div className="editor-toolbar">
            <span>
              <Code size={17} />
              Your solution
            </span>
            <select
              aria-label="Coding language"
              value={language}
              onChange={async (e) => {
                const next = e.target.value;
                if (user && saved === "Unsaved changes") {
                  try {
                    await api("/drafts/" + id, { language, code }, "PUT");
                  } catch (error) {
                    notify((error as Error).message);
                    return;
                  }
                }
                setLanguage(next);
              }}
            >
              <option value="java">Java</option>
              <option value="python">Python</option>
              <option value="cpp">C++</option>
            </select>
            <button
              className="icon-btn"
              aria-label="Save code draft"
              onClick={save}
              disabled={!user}
            >
              <FloppyDisk size={18} />
            </button>
            <small>{saved}</small>
          </div>
          <Suspense
            fallback={
              <textarea
                className="code-fallback"
                aria-label="Code editor"
                value={code}
                onChange={(e) => editCode(e.target.value)}
              />
            }
          >
            <CodeEditor value={code} onChange={editCode} language={language} />
          </Suspense>
          <div className="editor-actions">
            <span>
              <span className="blue-dot" />
              Make it work. Then make it clear.
            </span>
            <button
              className="button secondary small"
              disabled={busy}
              onClick={() => run.mutate(false)}
            >
              <Play size={15} />
              Run
            </button>
            <button
              className="button primary small"
              disabled={busy}
              onClick={() => run.mutate(true)}
            >
              <PaperPlaneTilt size={16} />
              {busy ? "Evaluating…" : "Submit"}
            </button>
          </div>
          <div className="results-panel">
            <div className="tabs">
              {["Test results", "Custom input", "Submissions"].map((t) => (
                <button
                  key={t}
                  className={resultTab === t ? "active" : ""}
                  onClick={() => setResultTab(t)}
                >
                  {t}
                </button>
              ))}
            </div>
            {resultTab === "Custom input" ? (
              <label className="custom-input-label">
                Input for the Run button
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={p.samples[0]?.input}
                />
              </label>
            ) : resultTab === "Submissions" ? (
              <div className="submission-list">
                {progress.submissions
                  .filter((s) => s.problem === id)
                  .slice()
                  .reverse()
                  .map((s) => (
                    <button
                      key={s.id}
                      onClick={() => {
                        setJob(s.id);
                        setResultTab("Test results");
                      }}
                    >
                      <span
                        className={s.status === "ACCEPTED" ? "success" : ""}
                      >
                        {s.status.replaceAll("_", " ")}
                      </span>
                      <span>{s.language}</span>
                      <small>{new Date(s.createdAt).toLocaleString()}</small>
                    </button>
                  ))}
                {!progress.submissions.some((s) => s.problem === id) && (
                  <p className="muted">Your submissions will be saved here.</p>
                )}
              </div>
            ) : submission.isError ? (
              <ErrorState error={submission.error} />
            ) : submission.data ? (
              <div className="test-results">
                <strong
                  className={
                    submission.data.status === "ACCEPTED" ? "success" : ""
                  }
                >
                  {submission.data.status.replaceAll("_", " ")}
                </strong>
                {submission.data.message && <p>{submission.data.message}</p>}
                {submission.data.results.map((r) => (
                  <details key={r.index}>
                    <summary>
                      <span className={r.status === "PASSED" ? "success" : ""}>
                        {r.status === "PASSED" ? (
                          <CheckCircle size={16} />
                        ) : (
                          <TerminalWindow size={16} />
                        )}
                        Test {r.index} {r.public ? "" : "· hidden"}
                      </span>
                      <span>{r.status.replaceAll("_", " ")}</span>
                    </summary>
                    {r.public ? (
                      <>
                        <small>Input</small>
                        <pre>{r.input}</pre>
                        <small>Your output</small>
                        <pre>{r.actual || "(empty)"}</pre>
                        {r.expected !== undefined && (
                          <>
                            <small>Expected</small>
                            <pre>{r.expected}</pre>
                          </>
                        )}
                      </>
                    ) : (
                      <p>
                        Hidden test data stays private. Try the public cases or
                        ask your tutor for edge-case ideas.
                      </p>
                    )}
                    {r.message && <pre>{r.message}</pre>}
                  </details>
                ))}
              </div>
            ) : (
              <div className="results-empty">
                <TerminalWindow size={25} />
                <span>Give your idea a test run.</span>
                <p>
                  Results will appear here. Your first attempt doesn’t have to
                  be your last.
                </p>
              </div>
            )}
          </div>
        </section>
      </div>
    </>
  );
}
