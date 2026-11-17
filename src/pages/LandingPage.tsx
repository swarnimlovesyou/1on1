import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight } from "@phosphor-icons/react";
import { api } from "../api";
import Experiment from "../components/Experiment";
import { familyStyle } from "../families";
import type { Scene } from "../types";
import { usePrep } from "./prep/usePrep";
import { useLessons } from "./Learning";

const demoScene: Scene = { algorithm: "sliding-window", input: "2, 1, 5, 1, 3, 2", target: 3 };

/** An original landscape: sky, soft clouds, three mountain ranges and a meadow. Colours come from CSS so night mode repaints it. */
function Landscape() {
  return (
    <svg className="meadow-landscape" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="meadow-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="var(--m-sky-top)" />
          <stop offset="0.62" stopColor="var(--m-sky-mid)" />
          <stop offset="1" stopColor="var(--m-sky-low)" />
        </linearGradient>
        <radialGradient id="meadow-sun" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="var(--m-sun)" stopOpacity="0.95" />
          <stop offset="1" stopColor="var(--m-sun)" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="meadow-grass" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="var(--m-grass-top)" />
          <stop offset="1" stopColor="var(--m-grass-low)" />
        </linearGradient>
        <linearGradient id="meadow-haze" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="var(--m-sky-low)" stopOpacity="0" />
          <stop offset="1" stopColor="var(--m-sky-low)" stopOpacity="0.75" />
        </linearGradient>
        <filter id="meadow-blur" x="-20%" y="-50%" width="140%" height="200%">
          <feGaussianBlur stdDeviation="18" />
        </filter>
      </defs>
      <rect width="1440" height="900" fill="url(#meadow-sky)" />
      <circle cx="1080" cy="250" r="260" fill="url(#meadow-sun)" />
      <circle className="meadow-moon" cx="1080" cy="210" r="34" />
      <g className="meadow-stars">
        {[[120, 90], [260, 60], [410, 120], [560, 50], [700, 140], [840, 70], [1230, 90], [1350, 160], [980, 300], [330, 260]].map(([x, y]) => (
          <circle key={x} cx={x} cy={y} r={x % 3 ? 1.4 : 2} />
        ))}
      </g>
      <g className="meadow-clouds" filter="url(#meadow-blur)">
        <ellipse cx="230" cy="170" rx="210" ry="46" />
        <ellipse cx="420" cy="215" rx="150" ry="34" />
        <ellipse cx="980" cy="120" rx="240" ry="40" />
        <ellipse cx="1250" cy="330" rx="200" ry="38" />
        <ellipse cx="620" cy="360" rx="180" ry="30" />
      </g>
      <path fill="var(--m-far)" d="M0 560 L120 470 L210 520 L330 420 L450 500 L560 430 L690 520 L800 445 L930 515 L1040 410 L1160 500 L1290 440 L1440 520 L1440 900 L0 900 Z" />
      <path fill="var(--m-snow)" opacity="0.7" d="M330 420 L370 447 L345 445 L330 432 L312 446 L292 448 Z M1040 410 L1080 440 L1052 437 L1040 424 L1024 438 L1003 440 Z" />
      <rect y="420" width="1440" height="200" fill="url(#meadow-haze)" />
      <path fill="var(--m-mid)" d="M0 640 L140 560 L260 610 L400 540 L540 620 L650 575 L790 640 L920 570 L1060 635 L1190 580 L1320 630 L1440 590 L1440 900 L0 900 Z" />
      <rect y="540" width="1440" height="140" fill="url(#meadow-haze)" opacity="0.6" />
      <path fill="var(--m-hill)" d="M0 700 C 200 650 380 690 560 670 C 760 648 900 700 1100 676 C 1250 660 1350 680 1440 670 L1440 900 L0 900 Z" />
      <path fill="url(#meadow-grass)" d="M0 760 C 260 730 520 770 760 748 C 1000 726 1220 760 1440 742 L1440 900 L0 900 Z" />
    </svg>
  );
}

export default function LandingPage() {
  const lessons = useLessons();
  const prep = usePrep();
  const bank = useQuery({ queryKey: ["bank-total"], queryFn: () => api<{ total: number }>("/bank?size=1"), staleTime: 300_000 });
  const figures = [
    [lessons.data?.length, "lessons, each with an animation you can step through"],
    [bank.data?.total, "practice questions, linked to where they live"],
    [prep.data?.guides.length, "Prep guides, from aptitude to system design"],
  ] as const;
  const navigate = useNavigate();
  const [topic, setTopic] = useState("");
  function ask(event: FormEvent) {
    event.preventDefault();
    navigate(topic.trim() ? "/learn?q=" + encodeURIComponent(topic.trim()).replace(/%20/g, "+") : "/learn");
  }
  return (
    <div className="landing2">
      <section className="meadow-hero">
        <Landscape />
        <header className="meadow-nav">
          <Link className="meadow-brand" to="/">
            <span className="brand-mark">1:1</span>
            1on1
          </Link>
          <nav aria-label="Site" className="meadow-pill">
            <Link to="/learn">Learn</Link>
            <Link to="/practice">Practise</Link>
            <Link to="/prep">Prep</Link>
            <Link to="/practice?tab=sheets">Sheets</Link>
          </nav>
          <div className="meadow-nav-end">
            <Link className="meadow-signin" to="/login">
              Sign in
            </Link>
            <Link className="meadow-glass" to="/signup">
              Get started
            </Link>
          </div>
        </header>
        <div className="meadow-copy">
          <p className="meadow-badge">
            {bank.data ? `${bank.data.total.toLocaleString("en-IN")} questions, ${lessons.data?.length ?? 33} animated lessons` : "Animated lessons and real practice"}
          </p>
          <h1>
            <span>Skip the noise.</span>
            <span className="meadow-fade">Make it click.</span>
          </h1>
          <p className="meadow-sub">
            Watch each algorithm work, one step and one sentence at a time. Then practise until you could explain it to someone else.
          </p>
          <form className="meadow-ask" onSubmit={ask} role="search">
            <input
              aria-label="What do you want to learn?"
              placeholder="What do you want to learn?"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
            <button type="submit">Start</button>
          </form>
          <Link className="meadow-first" to="/learn">
            Open your first notebook
          </Link>
        </div>
      </section>

      <main className="landing2-body">
        <dl className="landing-figures">
          {figures.map(([n, label]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{n === undefined ? "…" : n.toLocaleString("en-IN")}</dd>
            </div>
          ))}
        </dl>

        <section className="landing-demo">
          <div>
            <h2>Watch it work, then take the wheel.</h2>
            <p>
              Every animation runs the real algorithm in Java. Step forward, scrub back, change the input, and read what just happened in
              plain words. This one slides a window across six numbers.
            </p>
          </div>
          <div className="landing-demo-frame has-family" style={familyStyle("searching")}>
            <Experiment scene={demoScene} compact />
          </div>
        </section>

        <section className="ways-in" aria-labelledby="ways-in-title">
          <h2 id="ways-in-title">Three ways in</h2>
          <ul>
            <li>
              <Link to="/learn">
                <strong>Learn</strong>
                <span>Thirty-three lessons in prerequisite order, from arrays to max flow, each ending in questions graded as you go.</span>
              </Link>
            </li>
            <li>
              <Link to="/practice">
                <strong>Practise</strong>
                <span>Original problems with a coach, the Blind 75 and NeetCode 150 sheets, a bank you can filter by company, and timed mocks.</span>
              </Link>
            </li>
            <li>
              <Link to="/prep">
                <strong>Prep</strong>
                <span>Aptitude and reasoning with endless drills, puzzles with hints first, CS fundamentals and a system design playground.</span>
              </Link>
            </li>
          </ul>
        </section>

        <p className="landing-sources">
          Questions link to Codeforces, AtCoder, CSES and LeetCode; we keep titles and links, never their statements. Every list says where it
          came from.
        </p>
      </main>

      <footer className="landing2-footer">
        <p className="display">Start with one idea today.</p>
        <Link className="button primary" to="/learn">
          Open the library
        </Link>
      </footer>
    </div>
  );
}
