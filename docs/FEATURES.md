# 1on1 — consolidated feature catalogue

Last updated: 17 November 2026.

This document lists the product ideas agreed with the owner and, for each section, what is actually built. Each section opens with a **Status** line: **built** (implemented and covered by automated tests), **partial** (some items built, others not, with the reason), or **not built**. "Built" does not mean verified against live external services: live Judge0 execution, live Gemini answers and a PostgreSQL rehearsal are still open gates (see [Delivery boundaries](#delivery-boundaries-and-definition-of-completion)). Detailed evidence is in [PHASE2_HANDOFF.md](PHASE2_HANDOFF.md), [API.md](API.md), [the three-phase plan](IMPLEMENTATION_PLAN.md) and [VALIDATION.md](VALIDATION.md).

**Current verification (17 November 2026):** `npm run verify` passes: 149 backend tests, 40 frontend tests and the production build. The browser suite (95 specs) is being re-run; its result is not recorded here.

## Curriculum scope update

The core curriculum is implemented: 24 concepts in prerequisite order and 33 lessons (26 core lessons, including child lessons such as Quicksort, plus 7 advanced lessons: AVL, Dijkstra, max flow, trie, set cover, Quickselect, Bloom filter). The 7 advanced lessons now have full prose, objectives and four practice questions each. The skill tree was built as a concept map with an accessible list (section 1). See [the implemented curriculum](CURRICULUM.md).

## Product direction

**Make it click.** Help learners internalize DSA by manipulating visual models, connecting them to minimal code, recognizing patterns, solving problems, and revisiting mistakes.

The typical journey is:

**Concept map → visual mental model → minimal code → pattern drill → dry run → coding practice → reflection and spaced review.**

This is guidance, not a compulsory sequence. Lessons and experiments stay accessible without passing prerequisite checkpoints.

## 1. Home dashboard and concept map

**Status: built.** Concept map of the 24 concepts in prerequisite order (Kahn's algorithm) with a list view, evidence states, a next action and spaced review (`LearningMapService`, `pages/LearningMap.tsx`).

- An interactive map showing core concepts, their relationships, and recommended prerequisites.
- Freely accessible nodes with a simpler list view for small screens and accessibility.
- A personal next action: due review → today's plan task → next concept whose prerequisites have passed evidence → an unaccepted linked problem.
- Evidence-based states: new, explored, passed, accepted, each with the sentences that support it. No mastery percentages.
- Review urgency from correctness, hint use and elapsed time. Completed work remains recorded when a review becomes due.
- Autosaving or leaving a tab open does not count as studying.

## 2. Interactive concept notebooks

**Status: built.** 33 lessons with experiments, teaching sections, challenges and saved position. The Phase 2 handoff still lists minor trace issues as open (the Graphs trace keeps its array at -1, some traces label the input length `size` at step 0, the backtracking animation stops at five values).

- A visual mental model that can be manipulated before syntax.
- Teaching sections covering intuition, a worked example that follows the animation's own trace, the invariant, minimal implementation, complexity, and common mistakes.
- Code or pseudocode lines highlighted with the operation shown in the diagram.
- Prediction checkpoints and input-manipulation challenges, graded on the server.
- Links from a lesson to drills and coding problems.
- The current section, input, trace step and notes are saved so the learner can resume.
- Advanced lessons: full prose and four practice questions each, fact-checked against their traces.

## 3. Animated algorithm laboratory

**Status: built.** Java-generated traces rendered with shared playback controls; an Animations gallery shows every lesson's animation on one page.

- Operation animations for arrays and pointers, sliding windows, stacks and queues, linked lists, trees, heaps, graphs, DP tables, tries, set cover, Quickselect and Bloom filters.
- Stable identities for elements and nodes, including duplicate values.
- Play/pause, step forward/back, scrub, replay, speed controls, editable inputs and boundary-case presets.
- Synchronized explanation, variables and code highlighting.
- Java computes every trace; the frontend only renders it. Interactive inputs are capped at 32 values.
- **Animations gallery** (`/learn/animations`, `pages/Animations.tsx`): every animation in one place; each runs its Java trace only when the learner presses play, with a link back to the lesson.
- Keyboard operation and reduced motion.

## 4. Pattern-recognition drills

**Status: built.** Every core lesson has a pattern drill graded on the server (`ChallengeService`).

- Short "spot the pattern" exercises: a prompt and constraints, then the suitable pattern.
- Explanations of why an approach fits and why plausible alternatives fail.
- Missed drills feed the review schedule and link back to the lesson.

## 5. Dry-run and exam-practice mode

**Status: partial.** Dry runs graded against the real trace are built. Gemini explanations of mistakes are implemented but not verified live (no API key on the dev machine). Exam-style questions generated from uploaded materials are limited to editable revision cards (section 9). The Prep tracks below are built.

- Dry-run state tables checked field by field against the Java trace step; the first wrong field is reported.
- Graduated hints from the Blob; deterministic checks establish correctness.
- Attempts are saved for review.

### Prep tracks

**Status: built.** Five tracks at `/prep` (`PrepController`, `DrillService`, `scripts/prep/`, `pages/prep/`). Every content batch was fact-checked by a separate pass; guide quizzes are graded on the server.

- **CS fundamentals:** 30 guides with quizzes.
- **Aptitude:** 8 guides; **Reasoning:** 5 guides. Both link to drills across 13 topics. Drill questions are generated on the server from a seed, so a learner can draw as many as they like; the answer is never sent to the browser before grading.
- **Puzzles:** 20 puzzles. Two hints, then the solution. A typed answer is checked on the server.
- **System design:** 8 guides plus a traffic playground (`/prep/system-design/playground`) that models app servers as an M/M/c queue and the database as an M/M/1 queue. It is a teaching model, not a capacity planner.

These tracks cover general topics. They make no claim to match any particular exam or company's process.

## 6. Coding practice and real grading

**Status: partial.** Problems, editor, coach, question bank, sheets, mock assessments and contests are built. Live code execution is **not verified**: the Judge0 runner needs Docker, which is not available on the dev machine, so runs report the runner as unavailable. C++ references are missing for 52 problems, and the 8 that exist are unverified (no compiler).

- 60 original problems with statements, constraints, samples and lesson links. Each has a Python reference verified on every fixture, three hints, a full editorial and two hidden adversarial cases agreed by the Java and Python references.
- Java, Python and C++ editing with starter code and saved drafts per problem and language.
- Custom runs, sample tests, official submissions and submission history through Judge0. The pipeline (job persistence, restart recovery, hidden-case redaction, accepted-only credit) is covered by contract tests against a local fixture server, not a live sandbox.
- Accepted-only native solved credit, awarded once per problem.

### Guided coding coach

**Status: built** (live-run journey not verified, as above). A Coach tab per problem: plan (approach, invariant, worked example) → code → run → fix → reflect (`CoachService`, `components/CoachPanel.tsx`). Nudges come one at a time, built from the learner's own plan and actual run results; edited code marks old runs as stale. The worked solution needs an explicit confirm and comes with a transfer question. The coach never writes credit.

### Question bank, company pages and sheets

**Status: built** (`BankService`, `SheetController`, `pages/practice/`).

- **Question bank:** 16,331 external questions (Codeforces 11,526; AtCoder 2,943; LeetCode 1,462; CSES 400) beside 1on1's own 60. Titles, links, tags and ratings only, never statements. Filters for source, difficulty, topic and company; sorting by easiest, hardest or title.
- **Solve here** (`/practice/q/{id}`): an editor for an external question. The statement stays on its own site, and runs use the learner's own input only; there is no grading of external questions. Runs need the Judge0 runner.
- **Company pages:** 184 company lists from a community-reported LeetCode dataset (data as of May 2022). They show what people reported, not what a company asks today.
- **Blind 75 and NeetCode 150 sheets:** ticks (on the account when signed in, in the browser for guests), a link to the matching lesson, and up to five companies that most often reported each question.
- **LeetCode profile sync:** ticks sheet questions found among the profile's last 20 accepted submissions. It uses an unofficial endpoint and cannot see older history.
- **Mock OA:** timed assessments drawn from 1on1's own problems, scored only from official accepted runs within the window (so scoring also depends on the runner).

### Contests

**Status: built** (`ContestService`, `pages/contests/`). Upcoming Codeforces and AtCoder contests in the learner's local time, with a per-contest `.ics` calendar file. LeetCode and CodeChef are linked, not read. A failed source keeps its last good list and is shown as unavailable.

## 7. Own-code tracing and visual performance tools

### Trace my code

**Status: not built.** Tracing must run inside the isolated runner, and the Judge0 runner is not available on the dev machine. No AI-generated substitute is offered.

- Planned: step through the learner's real executed Python with line highlighting, variables, collections, references and mutations; capped traces with explicit truncation and unsupported-feature reports.

### Visual Big-O profiler

**Status: removed.** The performance lab that counted trace steps at four input sizes was removed in the November 2026 revamp: it showed little a learner could act on. Profiling the learner's own code still needs the isolated runner and is **not built**.

## 8. Contextual AI companion — "The Blob"

**Status: built; live answers not verified.** No Gemini key is configured on the dev machine, so the Blob is tested up to the provider boundary, and its answering states were checked in the browser with a stubbed reply (`TutorService`, `components/Tutor.tsx`).

- A clickable companion opening contextual chat beside the workspace, with posture for idle, thinking, answered, error and AI unavailable, and reduced-motion support.
- Suggestions fit the lesson step or the problem; a four-level "still stuck" ladder; an offline notice before typing.
- Coach plan, hints and run evidence go to the model; hidden test data and solution code do not.
- Natural-language requests for a visual example are validated and traced by Java.
- Conversations are saved per lesson or problem; responses can be cancelled.

## 9. Personal notebook and document-based exam preparation

**Status: built; live cited answers not verified** (no Gemini key; without one, the notebook returns the matching passages instead of an answer) (`NotebookService`, `workspace/DocumentNotebook.tsx`).

- Notes linked to lessons, problems and experiment snapshots.
- Text PDFs up to 10 MB and 100 pages; extraction keeps page numbers (PDFBox).
- Lucene BM25 search over the learner's own selected sources only, with file and page citations; the notebook says when the sources do not answer.
- Editable revision cards; self-reported recall is kept apart from graded results.
- Scanned, protected, oversized and non-PDF files are refused with a reason.

## 10. Claude, ChatGPT, and Codex integration through MCP

**Status: built; live clients not verified.** The MCP adapter (`mcp/server.mjs`, stdio transport) calls the Java API and owns no logic. Its tests run against a stub API, its smoke script against a running 1on1, and the pairing flow end to end in the browser (`tests/assistant-pairing.spec.ts`). A session inside Claude Desktop itself is not recorded here; Codex and ChatGPT were not tried.

- Built: seven public tools (`search_library`, `get_lesson` without answers, `run_trace`, `search_questions`, `upcoming_contests`, `get_drill`, `check_drill`).
- Built: **pairing.** Settings → Connect an assistant makes a revocable token, shown once and stored hashed. With it the adapter adds `my_context`, `search_my_notes`, `save_note` and `search_my_sources` (`AssistantController`); nothing paired can grade, change the account or read another learner.
- Built: the **Concept Coach**, **Exam Practice** and **Debugging Guide** skills (`mcp/skills/*/SKILL.md`), written to the teaching policy and these tools. Not yet run in a live assistant.
- Not built: browser updates pushed from the assistant (opening an experiment in the learner's tab).
- Planned order: Claude Desktop first, then ChatGPT and Codex against their actual connection requirements.
- External-assistant mode runs inside Claude/ChatGPT/Codex. The website's Blob keeps its own model integration.

References: [Claude local MCP](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop), [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## 11. Review, planning, and supporting platform features

**Status: built, with two unchecked parts:** the admin editor UI has only been type-checked (no local admin account was configured), and password-reset email needs SMTP configuration.

- Spaced review: successes return after 1, 3 and 7 days; a miss returns the next day; a hinted success repeats its interval (`ReviewSchedule`).
- Practice plans chosen by greedy set cover, with dated tasks, completion, rescheduling and regeneration that keeps finished work (`PlanService`).
- A progress page with notebooks explored, problems solved here, study streak, an activity heatmap and cohort summaries (`workspace/Analytics.tsx`).
- Accounts, sign-in, onboarding, password reset and preferences.
- Study cohorts with quartile summaries computed by randomized Quickselect.
- LeetCode public-profile connection with cached/stale/unavailable states; imported statistics stay separate from native credit.
- Administrator check, preview, draft and publish, with publication checks (`ContentChecks`, `AdminController`).

## 12. Visual personality and polish

**Status: built.**

- **One light theme** in the datalis visual language: Geist and Geist Mono, a pale green-grey page, white cards, ink text and a teal accent. The light/dark toggle was removed; a saved dark preference is ignored.
- **Landing page:** a live sliding-window animation framed as a browser window, a working percentages drill, live contests, and an interactive keyboard-shortcut grid.
- **Grouped sidebar with keys:** Learn (Home, Explore concepts, Animations), Practise (Practice, Sheets, Contests, Prep) and Your work (plan, notebook, progress, study together). Single-key shortcuts (H, L, A, P, S, C, R, N, G; `?` lists them) are ignored while typing.
- **Command palette:** Ctrl+K (⌘+K on macOS) jumps to any page, lesson, Prep track or guide, or sheet (`components/CommandPalette.tsx`).
- Loading, empty, unavailable and error states; keyboard access, reduced motion and phone layouts.
- No XP/level economy, compulsory unlocks or constant mascot movement.

## 13. November 2026 revamp

**Status: built.**

- **Python in the browser:** when no server runner is configured (as on free hosting), "Run" for Python executes in the learner's browser with Pyodide in a Web Worker: stdin from the custom input, stdout and tracebacks shown, a 10-second limit that stops runaway loops. It is never graded; official submissions and Java/C++ still need the server runner (`src/browserPython.ts`, `public/py-worker.js`).

- **Home dashboard:** the next step from the learning map, reviews due, streak, this week's count, an 84-day activity grid, live contests with countdowns, and questions other learners recently reported being asked ("I was asked this", `ReportController`).
- **Lesson flow:** what it is, why it matters, see it in action (animation with a follow-along transcript), the logic, its code, where it is used, how it connects (before and after concepts), then the check and practice.
- **Explore concepts:** family, difficulty and status filters kept in the URL; learning paths as a progress timeline with the next lesson marked; animations gallery with family filters and search.
- **Trace board:** 16 new concepts (union-find, topological sort, Kruskal, Bellman-Ford, Floyd-Warshall, segment and Fenwick trees, interval scheduling, bit manipulation, KMP, Rabin-Karp, monotonic stack and queue, 0/1 knapsack, LCS, matrix-chain interval DP) traced step by step in Java (`BoardTraces`) and drawn by one generic renderer (`BoardModel.tsx`): arrays, stacks, text with a sliding pattern, DP tables with the cells each value reads, and graphs.
- **Practice:** topic chips with counts; a quiz-style mock OA (15 or 30 aptitude, reasoning and CS questions, timed, graded on the server with a per-section score and review) beside the coding mock.
- **Prep guides:** Notes, Quiz and Sources tabs; free references checked to resolve; "Save as PDF" print layout; a per-track handbook of every guide's notes.
- **Plan it for me:** suggests topics, pace and difficulty from missed checks and solved problems; Gemini writes it when a key is set, constrained to real topics and validated, with a fixed-rule fallback (`PlanAdvisor`).
- **Progress:** where you've been (evidence states across concepts, families) and where you're heading (next step, the concepts now unlocked, the plan's finishing date and overdue tasks).
- **Study together:** a weekly circle problem (one the fewest members have solved, fixed for the ISO week) and member cards with this week's activity.

## Delivery boundaries and definition of completion

- **Local-first; public deployment is not required for this milestone.**
- **Docker Desktop only for the local judge.** Docker is not available on the dev machine, so live Judge0 runs, own-code tracing, own-code profiling and C++ reference checks remain blocked. This is recorded as a blocker, not as working grading.
- **Live Gemini** needs a locally configured key; it has not been checked on this machine.
- **PostgreSQL** is supported in schema and configuration; the live compatibility rehearsal needs the owner's database credentials and has not been run.
- **Java remains responsible for core algorithms and business logic.** The original trie, greedy set cover and randomized Quickselect, with their tests, baselines and three-size benchmarks, are preserved.
- **Verify real integrations and real behaviour.** Contract tests, catalogue counts or a visible interface alone do not demonstrate live AI, execution or educational quality.
- **Keep work local and unpushed** until the owner requests publication.
