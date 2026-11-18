import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowRight, Check, CheckCircle } from "@phosphor-icons/react";
import { api } from "../api";
import Experiment from "../components/Experiment";
import CompanyTags from "../components/CompanyTags";
import { familyStyle } from "../families";
import { SHORTCUTS } from "../shortcuts";
import type { Scene } from "../types";
import { usePrep } from "./prep/usePrep";
import { useLessons } from "./Learning";
import HeroStepper from "./landing/HeroStepper";

const demoScene: Scene = { algorithm: "sliding-window", input: "2, 1, 5, 1, 3, 2", target: 3 };

type SheetItem = { id: string; title: string; difficulty: string; companies?: { name: string; count: number }[] };
type Contest = { id: string; platform: string; title: string; start: string; url: string };
type Drill = { seed: number; prompt: string; unit?: string };

const PATHS = {
  "New to DSA": {
    note: "Start at the beginning; each step opens when the one before it makes sense.",
    steps: [
      ["Arrays and strings", "Indexes, scans, in-place updates"],
      ["Hash maps", "Remember what you have seen"],
      ["Two pointers and windows", "Throw away work you never needed"],
      ["Recursion and trees", "Trust the smaller call"],
    ],
  },
  "Preparing for placements": {
    note: "Already know the basics; you want reps that look like the real thing.",
    steps: [
      ["Blind 75 and NeetCode 150", "Ticked as you solve, with the lesson behind each one"],
      ["Company lists", "Questions people reported, filtered by company"],
      ["Timed mock assessment", "Aptitude, CS fundamentals and coding, on a clock"],
      ["Contests", "Codeforces and AtCoder, added to your calendar"],
    ],
  },
} as const;
type PathName = keyof typeof PATHS;

const KEY_DETAIL: Record<string, string> = {
  H: "Your next step, streak and what is happening this week.",
  L: "All 33 lessons, grouped by family, in prerequisite order.",
  A: "Every animation on one page, loaded when you press play.",
  P: "1on1 problems with a coach, the question bank and mocks.",
  S: "Blind 75 and NeetCode 150, with the companies that asked them.",
  C: "Upcoming Codeforces and AtCoder contests in your time zone.",
  R: "Aptitude, reasoning, puzzles, CS fundamentals and system design.",
  N: "Your own notes, tied to the lessons and problems they came from.",
  G: "What you have done, and what to do next.",
};

/** A real drill from the server: the answer stays there until you check. */
function LiveDrill() {
  const [answer, setAnswer] = useState("");
  const drill = useQuery({ queryKey: ["land-drill"], queryFn: () => api<Drill>("/drills/percentages/next"), retry: false, staleTime: Infinity });
  const check = useMutation({
    mutationFn: () => api<{ correct: boolean; expected: string }>("/drills/percentages/answer", { seed: drill.data!.seed, answer }),
  });
  if (!drill.data) return null;
  function submit(e: FormEvent) {
    e.preventDefault();
    if (answer.trim()) check.mutate();
  }
  return (
    <div className="land-card land-drill">
      <span className="land-eyebrow">Aptitude drill, checked on the server</span>
      <p className="land-drill-prompt">{drill.data.prompt}</p>
      <form onSubmit={submit}>
        <input
          aria-label="Your answer"
          value={answer}
          onChange={(e) => {
            setAnswer(e.target.value);
            check.reset();
          }}
          placeholder="Your answer"
        />
        <button className="button primary small" type="submit" disabled={!answer.trim() || check.isPending}>
          Check
        </button>
      </form>
      {check.data && (
        <p role="status" className={check.data.correct ? "land-ok" : "land-miss"}>
          {check.data.correct ? "Correct." : `Not quite. It's ${check.data.expected}${drill.data.unit === "%" ? "%" : ""}.`}
        </p>
      )}
    </div>
  );
}

export default function LandingPage() {
  const [path, setPath] = useState<PathName>("New to DSA");
  const [key, setKey] = useState("C");
  const lessons = useLessons();
  const prep = usePrep();
  const bank = useQuery({ queryKey: ["bank-total"], queryFn: () => api<{ total: number }>("/bank?size=1"), staleTime: 300_000, retry: false });
  const sheet = useQuery({ queryKey: ["sheet", "blind-75"], queryFn: () => api<{ items: SheetItem[] }>("/sheets/blind-75"), retry: false, staleTime: 300_000 });
  const contests = useQuery({ queryKey: ["contests"], queryFn: () => api<{ contests: Contest[] }>("/contests"), retry: false, staleTime: 600_000 });
  const row = sheet.data?.items.find((i) => i.id === "lc-two-sum") ?? sheet.data?.items[0];
  const count = (n: number | undefined, fallback: string) => (n === undefined ? fallback : n.toLocaleString("en-IN"));

  return (
    <div className="land">
      <header className="land-nav">
        <Link className="land-brand" to="/">
          <span className="brand-mark">1:1</span>
          1on1
        </Link>
        <nav aria-label="Site">
          <Link to="/learn">Learn</Link>
          <Link to="/practice">Practise</Link>
          <Link to="/prep">Prep</Link>
          <Link to="/contests">Contests</Link>
        </nav>
        <div className="land-nav-end">
          <Link to="/login">Sign in</Link>
          <Link className="button primary small" to="/learn">
            Start learning
          </Link>
        </div>
      </header>

      <main>
        <section className="land-hero">
          <div>
            <h1>
              Watch the algorithm work.
              <br />
              Make it click.
            </h1>
            <p>
              1on1 is a DSA and placement-prep workspace. Step through each algorithm one move at a time, answer questions that are graded
              as you go, then practise on real questions until you could explain it to someone else.
            </p>
            <div className="land-hero-actions">
            <div>
              <Link className="button primary" to="/learn">
                Start learning
              </Link>
              <Link className="button" to="/learn">
                Open your first notebook
              </Link>
            </div>
            <small>{count(lessons.data?.length, "49")} animated lessons. No sign-up needed to start.</small>
            </div>
          </div>
          <HeroStepper />
          <ul className="land-checks">
            {["Every algorithm animated", `${count(bank.data?.total, "16,000+")} practice questions`, "Answers graded on the server", "Placement prep built in"].map(
              (c) => (
                <li key={c}>
                  <Check size={15} weight="bold" aria-hidden="true" />
                  {c}
                </li>
              ),
            )}
          </ul>
        </section>

        <section className="land-frame" aria-label="1on1, working">
          <div className="land-window">
            <div className="land-window-bar" aria-hidden="true">
              <i />
              <i />
              <i />
              <span>1on1 / Sliding window</span>
            </div>
            <div className="land-window-body has-family" style={familyStyle("searching")}>
              <Experiment scene={demoScene} compact />
            </div>
          </div>
          {row && (
            <div className="land-float land-float-sheet">
              <span className="land-eyebrow">Blind 75</span>
              <strong>{row.title}</strong>
              <span className={"difficulty " + row.difficulty.toLowerCase()}>{row.difficulty}</span>
              <CompanyTags companies={row.companies} />
            </div>
          )}
          <div className="land-float land-float-check" aria-hidden="true">
            <CheckCircle size={18} weight="fill" />
            <span>
              Dry run graded from the trace
              <small>Step 7: sum = 8, best = 8</small>
            </span>
          </div>
        </section>

        <section className="land-section land-paths">
          <div className="land-section-head">
            <h2>Start where you are. The path keeps up.</h2>
            <p>The same lessons and questions underneath; what changes is the order you meet them in.</p>
          </div>
          <div className="land-tabs" role="tablist" aria-label="Who you are">
            {(Object.keys(PATHS) as PathName[]).map((p) => (
              <button key={p} role="tab" aria-selected={path === p} className={path === p ? "active" : ""} onClick={() => setPath(p)}>
                {p}
              </button>
            ))}
          </div>
          <div className="land-card land-path" role="tabpanel">
            <p className="muted">{PATHS[path].note}</p>
            <ol>
              {PATHS[path].steps.map(([title, detail], i) => (
                <li key={title}>
                  <span className="land-step">{i + 1}</span>
                  <span>
                    <strong>{title}</strong>
                    <small>{detail}</small>
                  </span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="land-section">
          <div className="land-section-head">
            <h2>The product, piece by piece</h2>
            <p>Everything below is running against the real app.</p>
          </div>
          <div className="land-grid">
            <LiveDrill />
            <div className="land-card land-contests">
              <span className="land-eyebrow">Upcoming contests, in your time zone</span>
              <ul>
                {(contests.data?.contests ?? []).slice(0, 4).map((c) => (
                  <li key={c.id}>
                    <time dateTime={c.start}>{new Date(c.start).toLocaleString(undefined, { weekday: "short", hour: "2-digit", minute: "2-digit" })}</time>
                    <span>
                      {c.title}
                      <small>{c.platform}</small>
                    </span>
                  </li>
                ))}
              </ul>
              <Link className="land-more" to="/contests">
                All contests
              </Link>
            </div>
            <div className="land-card">
              <span className="land-eyebrow">Prep</span>
              <strong className="land-big">{count(prep.data?.guides.length, "71")}</strong>
              <p className="muted">guides across aptitude, reasoning, puzzles, CS fundamentals and system design, each ending in a quiz.</p>
              <Link className="land-more" to="/prep">
                Open Prep
              </Link>
            </div>
            <div className="land-card">
              <span className="land-eyebrow">Sheets</span>
              <strong className="land-big">225</strong>
              <p className="muted">questions across Blind 75 and NeetCode 150, ticked as you solve and linked to the lesson that teaches each one.</p>
              <Link className="land-more" to="/practice?tab=sheets">
                Open the sheets
              </Link>
            </div>
          </div>
        </section>

        <section className="land-section land-keys">
          <div className="land-section-head">
            <h2>Keep your hands on the keyboard</h2>
            <p>Every area has a key. Press one, or tap it, to see what it opens.</p>
          </div>
          <div className="land-keygrid">
            {SHORTCUTS.map(([k, , label]) => (
              <button key={k} type="button" className={key === k ? "active" : ""} onClick={() => setKey(k)} aria-pressed={key === k}>
                <kbd>{k}</kbd>
                <span>{label}</span>
              </button>
            ))}
            <div className="land-keygrid-wide">
              <kbd>Ctrl K</kbd>
              <span>Jump to anything</span>
            </div>
          </div>
          <div className="land-key-detail" aria-live="polite">
            <kbd>{key}</kbd>
            <span>
              <strong>{SHORTCUTS.find(([k]) => k === key)?.[2]}</strong>
              {KEY_DETAIL[key]}
            </span>
          </div>
        </section>

        <section className="land-section">
          <div className="land-section-head">
            <h2>From first idea to proof you understand it</h2>
          </div>
          <ol className="land-timeline">
            {[
              ["See it", "Watch the real Java trace, one step and one sentence at a time."],
              ["Predict it", "Answer before the next step; a dry run is graded from the trace itself."],
              ["Write it", "Solve a problem with a coach that asks questions instead of handing over code."],
              ["Keep it", "Reviews come back when you are about to forget, not on a fixed schedule."],
            ].map(([t, d], i) => (
              <li key={t}>
                <span className="land-step">{i + 1}</span>
                <strong>{t}</strong>
                <p className="muted">{d}</p>
              </li>
            ))}
          </ol>
        </section>
      </main>

      <section className="land-cta">
        <h2>Start with one idea today.</h2>
        <Link className="button primary" to="/learn">
          Start learning <ArrowRight size={16} aria-hidden="true" />
        </Link>
      </section>
      <footer className="land-footer">
        <span>1on1</span>
        <span className="muted">Questions link to Codeforces, AtCoder, CSES and LeetCode; we keep titles and links, never their statements.</span>
      </footer>
    </div>
  );
}
