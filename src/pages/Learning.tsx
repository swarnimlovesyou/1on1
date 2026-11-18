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
import FamilyMark from "../components/FamilyMark";
import { FAMILIES, familyOfLesson, familyStyle, type FamilyId } from "../families";
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
export { default as Landing } from "./LandingPage";
export { default as Home } from "./home/Dashboard";

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
  // with no filter the collection reads as a book: one section per algorithm family
  const FAMILY_IDS = Object.keys(FAMILIES) as FamilyId[];
  const grouped =
    !!rows?.length &&
    tab === "All concepts" &&
    topic === "All topics" &&
    !path &&
    !q;
  const renderRow = (l: Lesson) => (
          <article className="concept-row" key={l.id}>
            <span className="concept-order">
              {String(l.order).padStart(2, "0")}
            </span>
            <Link to={"/learn/" + l.id} className="concept-main">
              <span className="concept-topic">
                <FamilyMark family={familyOfLesson(l)} />
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
          <Link className="prep-feature" to="/learn/animations">
            <strong>All animations</strong>
            <span>Every algorithm's step-by-step animation on one page, to play, step and scrub.</span>
          </Link>
          <div className="library-list-header">
            <span>The notebook collection</span>
            <span>{rows?.length} notebooks</span>
          </div>
          {grouped ? (
            FAMILY_IDS.map((family) => {
              const members = rows!.filter((l) => familyOfLesson(l) === family);
              return members.length ? (
                <section key={family} className="family-group">
                  <h2 className="family-heading">
                    <FamilyMark family={family} label />
                  </h2>
                  <div className="concept-list">{members.map(renderRow)}</div>
                </section>
              ) : null;
            })
          ) : (
            <div className="concept-list">{rows?.map(renderRow)}</div>
          )}
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
  const lessonsAll = useLessons();
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
  // the saved position seeds the experiment once per lesson; later saves must not reset what the learner is editing
  const openedScene = useRef<{ lesson?: string; scene?: Scene }>({});
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
    );
  if (openedScene.current.lesson !== l.id)
    openedScene.current = { lesson: l.id, scene: savedContext?.scene };
  const scene = activeScene ?? openedScene.current.scene ?? l.experiment,
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
          ["idea", "What it is"],
          ["why", "Why it matters"],
          ["experiment", "See it in action"],
          ["pattern", "The logic"],
          ["code", "Its code"],
          ["uses", "Where it's used"],
          ["connects", "How it connects"],
          ["checkpoint", "Check your intuition"],
          ["practice", "Make it stick"],
        ].map(([href, label]) => (
          <a key={href} href={"#" + href} onClick={() => setSection(href)}>
            {label}
          </a>
        ))}
      </aside>
      <article className="study-notebook has-family" style={familyStyle(familyOfLesson(l))}>
        <FamilyMark family={familyOfLesson(l)} label />
        <div className="notebook-breadcrumb">
          <Link to="/learn">Explore concepts</Link>
          <ArrowRight size={13} />
          <span>{FAMILIES[familyOfLesson(l)].label}</span>
          <Bookmark id={l.id} />
        </div>
        <h1 className="display">{l.title}</h1>
        <div className="notebook-facts">
          <span>
            <Clock size={15} />
            {l.minutes} min read & explore
          </span>
          <span>{l.difficulty}</span>
          <span>Notebook {String(l.order).padStart(2, "0")}</span>
        </div>
        {(() => {
          // a short lead first; the rest of the idea waits behind "Read the full idea"
          const sentences = l.body.split(/(?<=[.!?])\s+/);
          const lead = sentences.slice(0, 2).join(" ");
          const rest = sentences.slice(2).join(" ");
          const goals = l.teaching?.objectives ?? l.objectives ?? [];
          const prereqs = l.teaching?.prerequisites ?? [];
          return (
            <section id="idea" className="lesson-idea">
              <div className="idea-main">
                <h2>What it is</h2>
                <p className="lesson-prose lesson-lead">{lead}</p>
                {l.teaching?.mentalModel && (
                  <p className="mental-model">
                    <span>In one picture</span>
                    {l.teaching.mentalModel}
                  </p>
                )}
                {rest && (
                  <details className="read-more">
                    <summary>Read the full idea</summary>
                    <p className="lesson-prose">{rest}</p>
                  </details>
                )}
              </div>
              {(goals.length > 0 || prereqs.length > 0) && (
                <aside className="idea-side">
                  {goals.length > 0 && (
                    <>
                      <h3>You will be able to</h3>
                      <ul className="learn-goals">
                        {goals.map((goal) => (
                          <li key={goal}>{goal}</li>
                        ))}
                      </ul>
                    </>
                  )}
                  {prereqs.length > 0 && (
                    <>
                      <h3>Recommended first</h3>
                      <ul className="prerequisite-notes">
                        {prereqs.map((cid) => {
                          const concept = curriculum.data?.concepts.find((c) => c.id === cid);
                          return (
                            <li key={cid}>
                              {concept ? <Link to={"/learn/" + concept.lessonIds[0]}>{concept.title}</Link> : cid.replace("concept-", "").replaceAll("-", " ")}
                              {l.prerequisiteNotes?.[cid] && <small>{l.prerequisiteNotes[cid]}</small>}
                            </li>
                          );
                        })}
                      </ul>
                    </>
                  )}
                </aside>
              )}
            </section>
          );
        })()}
        {l.why && (
          <section id="why" className="why-card">
            <h2>Why it matters</h2>
            <p>{l.why}</p>
          </section>
        )}
        <section id="experiment">
          {savedContext?.scene && savedContext.step > 0 && savedContext.traceRevision !== 3 && (
            <p className="inline-alert">The visualization has been rebuilt. Your input is preserved; playback restarts from the beginning.</p>
          )}
          <div className="section-heading">
            <div>
              <h2>See it in action</h2>
              <p>{scene ? "Press play, or step through and predict each move before it happens." : "Follow the state changes in this worked model."}</p>
            </div>
            <Tutor lesson={l.id} experiment={contextScene ?? scene} step={step} onScene={setActiveScene} />
          </div>
          {(() => {
            const worked = l.blocks?.find((block) => block.id === "worked");
            const steps = (worked?.text ?? l.teaching?.workedExample ?? "").split(/(?<=[.!?])\s+/).filter(Boolean);
            return (
              <div className={"experiment-layout" + (steps.length ? " with-follow" : "")}>
                <div className="experiment-main">
                  {scene ? (
                    <Experiment
                      key={l.id}
                      scene={scene}
                      initialStep={activeScene ? 0 : savedContext?.traceRevision === 3 ? savedContext.step : 0}
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
                          {l.teaching.visualization.expectedStates.map((state, index) => (
                            <li key={index}>{state}</li>
                          ))}
                        </ol>
                        <p>{l.teaching.visualization.manipulation}</p>
                        <p className="muted">This worked example is read-only. An interactive canvas for this concept is not available yet.</p>
                      </div>
                    )
                  )}
                </div>
                {steps.length > 0 && (
                  <aside className="follow-along" aria-label="Follow along">
                    <h3>{worked?.title ?? "Follow along"}</h3>
                    <ol>
                      {steps.map((sentence, index) => (
                        <li key={index}>{sentence}</li>
                      ))}
                    </ol>
                  </aside>
                )}
              </div>
            );
          })()}
        </section>
        <section id="pattern">
          <h2>The logic</h2>
          <div className="pattern-grid">
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
            <div className="pitfall-card">
              <h3>Watch out for this</h3>
              <p className="lesson-prose">{l.pitfall}</p>
            </div>
          </div>
          {!!l.blocks?.filter((block) => block.id !== "worked").length && (
            <details className="go-deeper">
              <summary>Go deeper: why it works and what it costs</summary>
              {l.blocks
                ?.filter((block) => block.id !== "worked")
                .map((block) => (
                  <div className="lesson-block" key={block.id}>
                    <h3>{block.title}</h3>
                    <p className="lesson-prose">{block.text}</p>
                  </div>
                ))}
            </details>
          )}
        </section>
        {l.teaching && (
          <section id="code">
            <h2>Its code</h2>
            <p className="muted code-caption">{l.teaching.workedExample}</p>
            <div className="code-layout">
              <div className="code-main">
                <pre className="reference-code">{l.teaching.java.implementation}</pre>
                {l.teaching.java.lineAnnotations.length > 0 && (
                  <ul className="line-notes">
                    {l.teaching.java.lineAnnotations.map((annotation) => (
                      <li key={annotation.line}>
                        <span className="line-chip">Line {annotation.line}</span>
                        {annotation.explanation}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <aside className="code-side">
                <div>
                  <span>Time</span>
                  <strong>{l.teaching.complexity.time}</strong>
                </div>
                <div>
                  <span>Space</span>
                  <strong>{l.teaching.complexity.space}</strong>
                </div>
                <p className="muted">{l.teaching.complexity.assumptions}</p>
              </aside>
            </div>
          </section>
        )}
        {!!l.uses?.length && (
          <section id="uses">
            <h2>Where it's used</h2>
            <div className="use-grid">
              {l.uses.map((use) => (
                <div className="use-card" key={use.where}>
                  <strong>{use.where}</strong>
                  <p>{use.how}</p>
                </div>
              ))}
            </div>
            <p className="muted">
              Then use it yourself: the questions in <a href="#practice">Make it stick</a> are picked for this idea.
            </p>
          </section>
        )}
        {(() => {
          const before = (l.prerequisites ?? []).map((id) => lessonsAll.data?.find((x) => x.id === id)).filter(Boolean) as Lesson[];
          const after = (lessonsAll.data ?? []).filter((x) => x.prerequisites?.includes(l.id));
          return (
            <section id="connects">
              <h2>How it connects</h2>
              <div className="connect-row">
                <div className="connect-before">
                  <span>Builds on</span>
                  {before.length ? before.map((x) => <Link key={x.id} to={"/learn/" + x.id}>{x.title}</Link>) : <small>Nothing: a good place to start.</small>}
                </div>
                <div className="connect-now">
                  <span>This lesson</span>
                  <strong>{l.title}</strong>
                </div>
                <div className="connect-after">
                  <span>Unlocks</span>
                  {after.length ? after.map((x) => <Link key={x.id} to={"/learn/" + x.id}>{x.title}</Link>) : <small>The end of this branch.</small>}
                </div>
              </div>
            </section>
          );
        })()}
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
