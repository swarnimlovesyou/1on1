import { useState, useEffect, useRef } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  ArrowLeft,
  Clock,
  CheckCircle,
  BookOpen,
  Code,
  Compass,
  Play,
  Sparkle,
  BookmarkSimple,
  Check,
  Lightbulb,
  TreeStructure,
  Graph,
  BracketsCurly,
  ListBullets,
  MagnifyingGlass,
} from "@phosphor-icons/react";
import { api } from "../api";
import { useApp } from "../context";
import type {
  Lesson,
  Path,
  Problem,
  Scene,
  CurriculumManifest,
} from "../types";
import {
  Loading,
  ErrorState,
  PageHeading,
  Bookmark,
} from "../components/Shared";
import Experiment from "../components/Experiment";
import Tutor from "../components/Tutor";
import ChallengeCard from "../components/ChallengeCard";
import LinkedNotes from "../components/LinkedNotes";
import { ConceptMap, NextActionCard, ReviewsDue, useLearningMap } from "./LearningMap";
const sampleScene: Scene = {
  algorithm: "sliding-window",
  input: "2, 1, 5, 1, 3, 2",
  target: 3,
};
export const useLessons = () =>
  useQuery({ queryKey: ["lessons"], queryFn: () => api<Lesson[]>("/lessons") });
export const useProblems = () =>
  useQuery({
    queryKey: ["problems"],
    queryFn: () => api<Problem[]>("/problems"),
  });
function TopicIcon({ topic }: { topic: string }) {
  const Icon =
    topic === "Trees"
      ? TreeStructure
      : topic === "Graphs"
        ? Graph
        : topic === "Dynamic programming"
          ? BracketsCurly
          : topic === "Sorting"
            ? ListBullets
            : BookOpen;
  return <Icon size={21} weight="duotone" />;
}
export function Landing() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <Link className="brand" to="/">
          <span className="brand-mark">1:1</span>1on1
          <span className="brand-dot">.</span>
        </Link>
        <nav>
          <Link to="/learn">Explore concepts</Link>
          <Link to="/practice">Practice</Link>
          <Link to="/login">Sign in</Link>
          <Link className="button primary small" to="/signup">
            Find your flow <ArrowUpRight size={16} />
          </Link>
        </nav>
      </header>
      <main>
        <section className="landing-hero">
          <div>
            <h1>
              Don’t just learn it.
              <br /> <span>Make it click.</span>
            </h1>
            <p>
              Your own space to see algorithms unfold, ask the questions that
              matter, and turn “I think I get it” into “I’ve got this.”
            </p>
            <div className="landing-actions">
              <Link className="button primary" to="/learn">
                Open your first notebook <ArrowRight size={18} />
              </Link>
              <Link className="text-link" to="/home">
                Explore the workspace <ArrowUpRight size={16} />
              </Link>
            </div>
            <div className="landing-proof">
              <span>
                <Play size={16} />
                Interactive by design
              </span>
              <span>
                <Code size={16} />
                Real coding practice
              </span>
            </div>
          </div>
          <div className="landing-experiment">
            <div className="lesson-paper-label">
              <span className="blue-dot" />A page from your future notebook
              <span>Sliding window</span>
            </div>
            <Experiment scene={sampleScene} compact />
            <div className="margin-note">
              <Lightbulb size={20} />
              <span>
                Same window. One new value.
                <br /> <strong>A little less work, every time.</strong>
              </span>
            </div>
          </div>
        </section>
        <section className="landing-story">
          <h2>Understanding is a practice.</h2>
          <p>
            Read a little. Change an input. Follow the pointers. Ask why. Then
            try it yourself. 1on1 keeps the whole journey together.
          </p>
          <div className="landing-steps">
            {[
              [
                "See the idea",
                "24 core concepts, with worked visual models and supported interactive examples.",
              ],
              [
                "Make it yours",
                "A contextual tutor and a notebook for your own discoveries.",
              ],
              [
                "Put it to work",
                "60 original problems, a code editor, and honest feedback.",
              ],
            ].map(([h, p], i) => (
              <article key={h}>
                <span className="story-index">{i + 1}</span>
                <h3>{h}</h3>
                <p>{p}</p>
              </article>
            ))}
          </div>
          <Link className="button primary" to="/signup">
            Start your learning story <ArrowRight size={18} />
          </Link>
        </section>
      </main>
      <footer className="landing-footer">
        <strong>1on1.</strong>
        <span>A little progress. A lot of possibility.</span>
        <Link to="/learn">
          Keep exploring <ArrowUpRight size={16} />
        </Link>
      </footer>
    </div>
  );
}
export function Home() {
  const { user, progress } = useApp();
  const lessons = useLessons();
  const map = useLearningMap();
  const paths = useQuery({
    queryKey: ["paths"],
    queryFn: () => api<Path[]>("/paths"),
  });
  if (lessons.isLoading) return <Loading />;
  if (lessons.error)
    return <ErrorState error={lessons.error} retry={() => lessons.refetch()} />;
  const current =
    lessons.data?.find((l) => l.id === progress.resumeLesson) ??
    lessons.data?.find((l) => l.branch === "core") ??
    lessons.data?.[0];
  return (
    <>
      <div className="home-title">
        <h1>
          A little progress.
          <br /> <span>A lot of possibility.</span>
        </h1>
        <p>
          {user
            ? `${user.name.split(" ")[0]}, you don’t need to know it all today.`
            : "You don’t need to know it all today."}
          <br /> Just find the next thing that clicks.
        </p>
      </div>
      {map.data && (
        <div className="home-next">
          <NextActionCard action={map.data.nextAction} />
          <ReviewsDue />
        </div>
      )}
      <section className="continue-section">
        <div className="continue-copy">
          <h2>{current?.title}</h2>
          <p>{current?.body.split(". ").slice(0, 2).join(". ")}.</p>
          <div className="lesson-facts">
            <span>
              <Clock size={15} />
              {current?.minutes} min
            </span>
            <span>{current?.topics[0]}</span>
          </div>
          <Link className="button primary" to={"/learn/" + current?.id}>
            {progress.resumeLesson
              ? "Continue learning"
              : "Let’s make it click"}
            <ArrowRight size={18} />
          </Link>
        </div>
        {current?.experiment ? (
          <Experiment scene={current.experiment} compact />
        ) : (
          <div className="lesson-block">
            <h3>Follow the worked example</h3>
            <p>{current?.teaching?.workedExample}</p>
          </div>
        )}
      </section>
      <div className="learning-pulse">
        <span>
          <span className="pulse-symbol">
            <CheckCircle size={19} />
          </span>
          <strong>{progress.completed.length}</strong> notebooks explored
        </span>
        <span>
          <Code size={19} />
          <strong>{progress.solved.length}</strong> problems solved
        </span>
        <span>
          <BookmarkSimple size={19} />
          <strong>{progress.bookmarks.length}</strong> saved for later
        </span>
        <Link to="/progress">
          Your learning story <ArrowUpRight size={16} />
        </Link>
      </div>
      <section className="home-lower">
        <div>
          <div className="section-heading">
            <h2>Your next lightbulb moment</h2>
            <Link to="/learn">
              Explore all <ArrowUpRight size={15} />
            </Link>
          </div>
          <div className="lesson-rows">
            {lessons.data
              ?.filter((l) => !progress.completed.includes(l.id))
              .slice(0, 4)
              .map((l) => (
                <Link key={l.id} to={"/learn/" + l.id} className="lesson-row">
                  <span className="topic-symbol">
                    <TopicIcon topic={l.topics[0]} />
                  </span>
                  <span>
                    <strong>{l.title}</strong>
                    <small>
                      {l.topics[0]} <span>·</span> {l.minutes} min notebook
                    </small>
                  </span>
                  <ArrowUpRight size={18} />
                </Link>
              ))}
          </div>
        </div>
        <div>
          <div className="section-heading">
            <h2>A path, not a checklist</h2>
            <Compass size={20} />
          </div>
          <div className="path-rows">
            {paths.data?.map((p, i) => (
              <Link to={"/learn?path=" + p.id} key={p.id} className="path-row">
                <span className={"path-marker path-" + i}>
                  <Compass size={22} />
                </span>
                <div>
                  <h3>{p.title}</h3>
                  <p>{p.lessons.length} connected notebooks</p>
                  <div className="progress-line">
                    <span
                      style={{
                        width:
                          (p.lessons.filter((id) =>
                            progress.completed.includes(id),
                          ).length /
                            p.lessons.length) *
                            100 +
                          "%",
                      }}
                    />
                  </div>
                </div>
                <ArrowRight size={17} />
              </Link>
            ))}
          </div>
        </div>
      </section>
      <div className="quiet-callout">
        <Sparkle size={22} />
        <div>
          <strong>Stuck is a starting point.</strong>
          <p>
            Your 1on1 tutor is right inside every notebook. Ask the question you
            were about to skip.
          </p>
        </div>
        <Link to="/learn/lesson-sliding-window">
          Meet your thinking partner <ArrowRight size={17} />
        </Link>
      </div>
    </>
  );
}
export function Library() {
  const { progress } = useApp(),
    [params, setParams] = useSearchParams();
  const lessons = useLessons(),
    paths = useQuery({
      queryKey: ["paths"],
      queryFn: () => api<Path[]>("/paths"),
    });
  const [tab, setTab] = useState("All concepts"),
    [topic, setTopic] = useState("All topics"),
    [q, setQ] = useState(params.get("q") ?? "");
  const path = paths.data?.find((p) => p.id === params.get("path"));
  const search = useQuery({
    queryKey: ["search", q],
    queryFn: () =>
      api<(Lesson | Problem)[]>("/search?q=" + encodeURIComponent(q)),
    enabled: !!q,
  });
  if (lessons.isLoading) return <Loading />;
  if (lessons.error) return <ErrorState error={lessons.error} />;
  const topics = [
    "All topics",
    ...new Set(lessons.data?.flatMap((l) => l.topics)),
  ];
  const rows = lessons.data?.filter(
    (l) =>
      (topic === "All topics" || l.topics.includes(topic)) &&
      (!path || path.lessons.includes(l.id)) &&
      (tab !== "Saved for later" || progress.bookmarks.includes(l.id)) &&
      (!q || search.data?.some((r) => r.id === l.id)),
  );
  return (
    <>
      <PageHeading
        title={path?.title ?? "Make the idea click."}
        description={
          path?.description ??
          "A collection of little experiments, big ideas, and moments of understanding."
        }
        action={
          <span className="collection-count">
            <BooksCount />
            {lessons.data?.length ?? 0} notebooks to explore
          </span>
        }
      />
      <div className="library-toolbar">
        <div className="tabs">
          {["All concepts", "Concept map", "Learning paths", "Saved for later"].map((t) => (
            <button
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => {
                setTab(t);
                setParams({});
              }}
            >
              {t}
              {t === "Saved for later" && (
                <span>{progress.bookmarks.length}</span>
              )}
            </button>
          ))}
        </div>
        <div className="search-field">
          <MagnifyingGlass size={17} />
          <input
            aria-label="Search the learning library"
            placeholder="Search a concept or topic…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </div>
      {tab === "Concept map" ? (
        <ConceptMap />
      ) : tab === "Learning paths" ? (
        <div className="learning-paths">
          {paths.data?.map((p, i) => (
            <Link
              key={p.id}
              to={"/learn?path=" + p.id}
              onClick={() => setTab("All concepts")}
              className="learning-path"
            >
              <span className={"path-marker path-" + i}>
                <Compass size={28} />
              </span>
              <h2>{p.title}</h2>
              <p>{p.description}</p>
              <span>
                {p.lessons.length} notebooks <ArrowRight size={17} />
              </span>
            </Link>
          ))}
        </div>
      ) : (
        <>
          <div className="topic-filters">
            {topics.map((t) => (
              <button
                key={t}
                className={topic === t ? "active" : ""}
                onClick={() => setTopic(t)}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="library-list-header">
            <span>THE NOTEBOOK COLLECTION</span>
            <span>{rows?.length} notebooks</span>
          </div>
          <div className="concept-list">
            {rows?.map((l) => (
              <article className="concept-row" key={l.id}>
                <span className="concept-order">
                  {String(l.order).padStart(2, "0")}
                </span>
                <Link to={"/learn/" + l.id} className="concept-main">
                  <span className="concept-topic">
                    {l.topics[0]}
                    <span> / </span>
                    {l.subtitle}
                  </span>
                  <h2>{l.title}</h2>
                  <p>{l.body.slice(0, 118)}…</p>
                  <div className="concept-meta">
                    <span>
                      <Clock size={14} />
                      {l.minutes} min
                    </span>
                    <span>{l.difficulty}</span>
                    <span className="concept-complexity">
                      {l.timeComplexity}
                    </span>
                  </div>
                </Link>
                <div className="concept-actions">
                  {progress.completed.includes(l.id) && (
                    <span className="complete-badge">
                      <CheckCircle size={17} />
                      Explored
                    </span>
                  )}
                  <Bookmark id={l.id} />
                  <Link
                    aria-label={"Open " + l.title}
                    className="open-concept"
                    to={"/learn/" + l.id}
                  >
                    <ArrowUpRight size={21} />
                  </Link>
                </div>
              </article>
            ))}
          </div>
          {!rows?.length && (
            <div className="empty">
              <BookOpen size={35} />
              <h2>
                {tab === "Saved for later"
                  ? "Keep a good idea close."
                  : "No concepts match yet."}
              </h2>
              <p>
                {tab === "Saved for later"
                  ? "Bookmark a concept to find it here when you’re ready."
                  : "Try a different topic or search prefix."}
              </p>
            </div>
          )}
        </>
      )}
    </>
  );
}
function BooksCount() {
  return <BookOpen size={18} />;
}
export function NotebookPage() {
  const { id } = useParams(),
    { user, progress, progressReady, notify, reload } = useApp();
  const [sceneParams] = useSearchParams();
  const curriculum = useQuery({
    queryKey: ["curriculum"],
    queryFn: () => api<CurriculumManifest>("/curriculum"),
  });
  const query = useQuery({
      queryKey: ["lesson", id],
      queryFn: () => api<Lesson>("/lessons/" + id),
    }),
    problems = useProblems();
  const [note, setNote] = useState(""),
    [section, setSection] = useState("idea"),
    [activeScene, setActiveScene] = useState<Scene>(),
    [contextScene, setContextScene] = useState<Scene>(),
    [traceRevision, setTraceRevision] = useState<number>(),
    [step, setStep] = useState(0);
  useEffect(() => {
    setActiveScene(undefined);
    setContextScene(undefined);
    setSection(window.location.hash.slice(1) || "idea");
    setStep(0);
    const encoded = sceneParams.get("scene");
    if (encoded && encoded.length < 3000) {
      try {
        const parsed = JSON.parse(encoded);
        if (
          "lesson-" + parsed.algorithm === id &&
          typeof parsed.input === "string"
        )
          setActiveScene(parsed);
      } catch {
        notify(
          "That saved experiment could not be opened. The original lesson is available.",
        );
      }
    }
  }, [id, sceneParams.get("scene")]);
  const update = useMutation({
    mutationFn: (b: unknown) => api("/progress", b),
    onSuccess: () => reload(),
    onError: (e) => notify(e.message),
  });
  const lastResume = useRef("");
  useEffect(() => {
    if (!user || !query.data || (!contextScene && query.data.experiment))
      return;
    const context = {
      version: 1,
      lesson: id,
      scene: contextScene,
      step,
      section,
      codeRevision: "",
      traceRevision,
    };
    const key = JSON.stringify(context);
    if (lastResume.current === key) return;
    const timer = setTimeout(() => {
      api("/study-context/" + id, context, "PUT")
        .then(() => {
          lastResume.current = key;
        })
        .catch((error) =>
          notify("Your study position could not be saved. " + error.message),
        );
    }, 700);
    return () => clearTimeout(timer);
  }, [
    user?.id,
    id,
    step,
    section,
    JSON.stringify(contextScene),
    query.data?.id,
    traceRevision,
  ]);
  if (query.isLoading || (user && !progressReady)) return <Loading />;
  if (query.error || !query.data) return <ErrorState error={query.error} />;
  const l = query.data,
    savedContext = progress.studyContexts?.find(
      (context) => context.lesson === l.id,
    ),
    scene = activeScene ?? savedContext?.scene ?? l.experiment,
    completed = progress.completed.includes(l.id);
  const related = problems.data
    ?.filter((p) =>
      l.linkedProblems
        ? l.linkedProblems.includes(p.id)
        : p.topics.some((t) => l.topics.includes(t)),
    )
    .sort(
      (a, b) =>
        Number(
          b.topics.some((t) => t.toLowerCase() === l.subtitle.toLowerCase()),
        ) -
        Number(
          a.topics.some((t) => t.toLowerCase() === l.subtitle.toLowerCase()),
        ),
    )
    .slice(0, 3);
  return (
    <div className="notebook-layout">
      <aside className="chapter-nav">
        <Link to="/learn" className="back-link">
          <ArrowLeft size={16} />
          All concepts
        </Link>
        <span className="chapter-label">Inside this notebook</span>
        {[
          ["idea", "The idea"],
          ["experiment", "See it in action"],
          ["code", "Connect it to code"],
          ["pattern", "The pattern"],
          ["checkpoint", "Check your intuition"],
          ["practice", "Make it stick"],
        ].map(([href, label]) => (
          <a key={href} href={"#" + href} onClick={() => setSection(href)}>
            {label}
          </a>
        ))}
        <div className="chapter-bottom">
          <span>Space to be curious.</span>
          <p>You can change the input, break an assumption, and start again.</p>
        </div>
      </aside>
      <article className="study-notebook">
        <div className="notebook-breadcrumb">
          <span>{l.topics[0]}</span>
          <ArrowRight size={13} />
          {l.subtitle}
          <Bookmark id={l.id} />
        </div>
        <h1>{l.title}</h1>
        <div className="notebook-facts">
          <span>
            <Clock size={15} />
            {l.minutes} min read & explore
          </span>
          <span>{l.difficulty}</span>
          <span>Notebook {String(l.order).padStart(2, "0")}</span>
        </div>
        <section id="idea">
          <h2>The idea</h2>
          <p className="lesson-prose">{l.body}</p>
          {l.teaching && (
            <>
              <h3>What you will learn</h3>
              <ul>
                {l.teaching.objectives.map((objective) => (
                  <li key={objective}>{objective}</li>
                ))}
              </ul>
              {!!l.teaching.prerequisites.length && (
                <p>
                  Recommended first:{" "}
                  {l.teaching.prerequisites.map((cid, index) => {
                    const concept = curriculum.data?.concepts.find(
                      (c) => c.id === cid,
                    );
                    return (
                      <span key={cid}>
                        {index > 0 ? ", " : ""}
                        {concept ? (
                          <Link to={"/learn/" + concept.lessonIds[0]}>
                            {concept.title}
                          </Link>
                        ) : (
                          cid.replace("concept-", "").replaceAll("-", " ")
                        )}
                      </span>
                    );
                  })}
                </p>
              )}
            </>
          )}
          {l.blocks
            ?.filter((block) => block.id === "worked")
            .map((block) => (
              <div className="lesson-block" key={block.id}>
                <h3>{block.title}</h3>
                <p className="lesson-prose">{block.text}</p>
              </div>
            ))}
        </section>
        <section id="experiment">
          {savedContext?.scene &&
            savedContext.step > 0 &&
            savedContext.traceRevision !== 3 && (
              <p className="inline-alert">
                The visualization has been rebuilt. Your input is preserved;
                playback restarts from the beginning.
              </p>
            )}
          <div className="section-heading">
            <div>
              <h2>What if you could see it?</h2>
              <p>
                {scene
                  ? "Step through slowly. Then make it your own."
                  : "Follow the state changes in this worked model."}
              </p>
            </div>
            <Tutor
              lesson={l.id}
              experiment={contextScene ?? scene}
              step={step}
              onScene={setActiveScene}
            />
          </div>
          {scene ? (
            <Experiment
              key={l.id}
              scene={scene}
              initialStep={
                activeScene
                  ? 0
                  : savedContext?.traceRevision === 3
                    ? savedContext.step
                    : 0
              }
              code={l.code}
              onStep={(s, index, revision) => {
                setStep(index);
                setContextScene(s);
                setTraceRevision(revision);
              }}
            />
          ) : (
            l.teaching && (
              <div className="lesson-block">
                <h3>{l.teaching.visualization.exampleInput}</h3>
                <ol>
                  {l.teaching.visualization.expectedStates.map(
                    (state, index) => (
                      <li key={index}>{state}</li>
                    ),
                  )}
                </ol>
                <p>{l.teaching.visualization.manipulation}</p>
                <p className="muted">
                  This worked example is read-only. An interactive canvas for
                  this concept is not available yet.
                </p>
              </div>
            )
          )}
        </section>
        {l.teaching && (
          <section id="code">
            <h2>Minimal Java: {l.teaching.title}</h2>
            <p className="lesson-prose">{l.teaching.workedExample}</p>
            <pre className="reference-code">
              {l.teaching.java.implementation}
            </pre>
            {l.teaching.java.lineAnnotations.map((annotation) => (
              <p key={annotation.line}>
                <strong>Line {annotation.line}:</strong>{" "}
                {annotation.explanation}
              </p>
            ))}
            <p>
              <strong>Time:</strong> {l.teaching.complexity.time}.{" "}
              <strong>Space:</strong> {l.teaching.complexity.space}.
            </p>
            <p className="muted">{l.teaching.complexity.assumptions}</p>
          </section>
        )}
        <section id="pattern">
          <h2>The pattern to hold onto</h2>
          <div className="insight">
            <Lightbulb size={22} />
            <p>{l.invariant}</p>
          </div>
          <div className="complexity-row">
            <div>
              <span>Time</span>
              <strong>{l.timeComplexity}</strong>
            </div>
            <div>
              <span>Space</span>
              <strong>{l.spaceComplexity}</strong>
            </div>
          </div>
          <h3>Watch out for this</h3>
          <p className="lesson-prose">{l.pitfall}</p>
          {l.blocks
            ?.filter((block) => block.id !== "worked")
            .map((block) => (
              <div className="lesson-block" key={block.id}>
                <h3>{block.title}</h3>
                <p className="lesson-prose">{block.text}</p>
              </div>
            ))}
        </section>
        <div id="checkpoint" className="lesson-challenges">
          <h2>Try the idea yourself.</h2>
          <p className="muted">
            Predict, change an input, recognise the pattern, and trace a state.
          </p>
          {l.challenges.map((challenge) => (
            <ChallengeCard
              key={challenge.id}
              challenge={challenge}
              scene={contextScene ?? scene}
            />
          ))}
        </div>
        <section>
          <h2>In your own words</h2>
          <p className="muted">
            The explanation you write yourself is the one that stays.
          </p>
          <label className="sr-only" htmlFor="lesson-note">
            Personal lesson note
          </label>
          <textarea
            id="lesson-note"
            className="note-input"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Something clicked when…"
          />
          <div className="note-actions">
            <span>Your notes are private.</span>
            <button
              className="button secondary small"
              disabled={!note.trim()}
              onClick={async () => {
                try {
                  await api("/notes", {
                    title: l.subtitle + " — my understanding",
                    text: note,
                    lesson: l.id,
                    experiment: contextScene ?? scene,
                  });
                  setNote("");
                  reload();
                  notify("Saved to your notebook");
                } catch (e) {
                  notify((e as Error).message);
                }
              }}
            >
              Save thought <BookmarkSimple size={15} />
            </button>
          </div>
          <LinkedNotes lesson={l.id} />
        </section>
        <section id="practice">
          <h2>Understanding loves a little practice.</h2>
          {l.teaching && (
            <>
              <h3>Apply this concept</h3>
              {curriculum.isPending ? (
                <p role="status">Loading selected questions…</p>
              ) : curriculum.error ? (
                <ErrorState
                  error={curriculum.error}
                  retry={() => curriculum.refetch()}
                />
              ) : (
                l.teaching.applications.map((app) => {
                  const question = curriculum.data?.questions.find(
                    (q) => q.id === app.questionId,
                  );
                  if (!question) return null;
                  return (
                    <div className="lesson-block" key={app.questionId}>
                      <h4>
                        {question.canonicalUrl ? (
                          <a
                            href={question.canonicalUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {question.title} <ArrowUpRight size={15} />
                          </a>
                        ) : question.localProblemId ? (
                          <Link to={"/practice/" + question.localProblemId}>
                            {question.title}
                          </Link>
                        ) : (
                          question.title
                        )}
                      </h4>
                      <p>{app.connection}</p>
                      {!!app.additionalPrerequisites.length && (
                        <p className="muted">
                          Also learn:{" "}
                          {app.additionalPrerequisites
                            .map(
                              (cid) =>
                                curriculum.data?.concepts.find(
                                  (c) => c.id === cid,
                                )?.title ?? cid,
                            )
                            .join(", ")}
                          .
                        </p>
                      )}
                      {!question.canonicalUrl && !question.localProblemId && (
                        <p className="muted">
                          Guided exercise: {question.approachOutline}
                        </p>
                      )}
                    </div>
                  );
                })
              )}
              <h3>Existing in-app practice</h3>
            </>
          )}
          <div className="related-problems">
            {related?.map((p) => (
              <Link key={p.id} to={"/practice/" + p.id}>
                <Code size={18} />
                <span>{p.title}</span>
                <span className={"difficulty " + p.difficulty.toLowerCase()}>
                  {p.difficulty}
                </span>
                <ArrowUpRight size={17} />
              </Link>
            ))}
          </div>
          <div className="notebook-finish">
            <div>
              <strong>One more idea, understood.</strong>
              <p>Take a moment to let it settle.</p>
            </div>
            <button
              className={"button " + (completed ? "secondary" : "primary")}
              onClick={() =>
                user
                  ? update.mutate({
                      completed: completed
                        ? progress.completed.filter((x) => x !== l.id)
                        : [...progress.completed, l.id],
                      resumeLesson: l.id,
                      resumeStep: step,
                    })
                  : notify("Sign in to save this milestone.")
              }
              disabled={update.isPending}
            >
              {completed ? (
                <>
                  <Check size={18} />
                  Explored
                </>
              ) : (
                <>
                  Mark as explored <CheckCircle size={18} />
                </>
              )}
            </button>
          </div>
        </section>
      </article>
    </div>
  );
}
