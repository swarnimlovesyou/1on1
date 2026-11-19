# Demonstration and assessment evidence

> Refreshed 19 November 2026. Feature status: [FEATURES.md](FEATURES.md). Technical detail: [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md). Live Judge0 runs and own-code tracing are not available on the demo machine; live tutor answers need a Groq key; the script shows those states honestly instead of skipping past them.

## Before the demo

- Run `npm run dev:core` (Vite on port 5173, API on 8080). Open `http://localhost:5173` in a fresh window.
- For live tutor answers, put a free `GROQ_API_KEY` (console.groq.com) in `.env` before starting. Without it the tutor shows its "not configured" state.
- Create a student account in advance and use it for a few real actions (a lesson, a drill, a quiz), so Home and Progress have activity. Do not seed fake activity.
- The machine needs internet for the contests page. If a source is down, the page says so; that is part of the demo.
- Keep a second tab open on `/learn/animations` in case the network is slow.

## Twelve-to-fourteen-minute flow

Times are cumulative. "Click" is what to do; "Say" is one or two lines.

### 1. Landing (0:00–0:45)

- **Click:** open `/`. Let the binary search on the right step through to 42, then scroll to the live sliding-window frame.
- **Say:** "1on1 joins a visual explanation, the code, practice and review in one place. Every algorithm state you will see is computed by Java, not drawn by hand."

### 2. Home and the lesson flow (0:45–2:30)

- **Click:** sign in. On Home, point at the next step, streak, activity, live contests and "Recently asked". Press `?` to show the keyboard shortcuts, then `L`.
- **Say:** "49 lessons in seven families. Filters live in the URL; learning paths show what's done and what's next."
- **Click:** open Sliding Window. Walk the chapters: what it is, why it matters, see it in action, the logic, its code, where it's used, how it connects.
- **Click:** in the experiment, change the input (e.g. `4, 4, 4, 1`), then play, step back, scrub.
- **Say:** "The trace comes from the Java trace engine; the browser only renders it. The follow-along text names each move."

### 3. Lesson practice (2:30–3:30)

- **Click:** answer a prediction question wrong, read the feedback, then answer correctly. Fill one dry-run field.
- **Say:** "Answers are graded on the server; the browser never receives the answer key. A miss schedules a review for tomorrow; successes return after 1, 3 and 7 days."

### 4. A new concept on the trace board (3:30–4:30)

- **Click:** Explore concepts → 0/1 Knapsack → See it in action. Step through the table. Then open Kruskal and step until an edge is rejected.
- **Say:** "Sixteen new concepts, from union-find to interval DP, share one renderer: arrays, stacks, tables and graphs, all sent by the Java trace. Each table cell shows the cells it read."

### 5. Practice: problems, sheets, bank, mock (4:30–7:00)

- **Click:** Practice → Problems; pick a topic chip. Then Sheets → Blind 75; tick a question.
- **Click:** Question bank: set Company to a large company, Sort → Hardest first.
- **Say:** "About 16,000 questions from Codeforces, AtCoder, CSES and LeetCode metadata: titles and links only, never statements. Company tags are community-reported and dated; learners' own 'I was asked this' reports appear only once two agree or the company is known."
- **Click:** Mock OA → Quiz → Start the quiz. Answer two, refresh the page to show it survives, then Submit → Submit anyway.
- **Say:** "Aptitude, reasoning and CS fundamentals on a clock, graded on the server with a section score and a review of every question."

### 6. Contests and Prep (7:00–9:30)

- **Click:** Contests: filter by AtCoder, "Add to calendar".
- **Click:** Prep → CS fundamentals → Deadlocks: show Notes, Quiz and Sources, press "Save as PDF". Back on the track, open the handbook.
- **Click:** Prep → Aptitude → Percentages → "Practise with unlimited questions"; answer `15%`.
- **Say:** "Each drill question is generated from a seed; the server regenerates it to grade, so the answer is never sent first."
- **Click:** System design → Traffic playground. Raise the load until the app tier is the bottleneck, then add servers and a cache.

### 7. Plan, progress and study together (9:30–11:30)

- **Click:** My practice plan → Plan it for me: goal, weeks, time a day → Suggest my plan → Build this plan.
- **Say:** "Topics come from the checks you missed and the problems you haven't solved. With a Groq key the AI writes the suggestion, but only real topics and in-range values are kept; without one, a fixed rule does it. Greedy set cover then picks few problems that cover every topic."
- **Click:** Progress: "Where you've been" and "Where you're heading".
- **Click:** Study together: create a circle; show this week's circle problem and the member cards.

### 8. Assistants (11:30–12:30)

- **Click:** Settings → Connect an assistant → Make a token. Show the settings block, then Revoke.
- **Say:** "An MCP adapter lets an assistant such as Claude use 1on1: lessons, traces, the bank, drills, and, once paired, this learner's next step and notes. The token is shown once, stored hashed, and revoking stops it at once. Three teaching skills ship with it."

### 9. Close (12:30–13:15)

- **Say:** "Not shown because they need services we don't have here: running your own code needs the Judge0 runner (free hosted plan or Docker); own-code tracing needs that runner too; the PostgreSQL rehearsal needs a database. Deployment is set up for Vercel, Render and Neon but not yet live. Tests: 175 backend and 46 frontend tests pass, plus browser tests for every area."

## Requirement mapping

| Requirement | Evidence |
| --- | --- |
| Genuine application workflow | Lesson → experiment → graded challenges → review schedule → practice → progress. |
| Java backend and own business logic | Spring controllers and services, custom algorithm classes, deterministic Java traces, server-side grading of challenges, drills and puzzles. |
| Working frontend integration | Same-origin API client with sessions/CSRF; production build; browser suite (95 specs, being re-run). |
| Two or more distinct techniques, Units 4–6 | Trie (search), greedy set cover (practice plans), randomized Quickselect (cohort quartiles). |
| Meaningful CO5 | Independent cohort-summary selection and scaled Quickselect comparison. |
| Inputs/outputs/assumptions/failures | API contracts, trace limits, infeasible plan coverage, contest source failures, runner and provider unavailable states. |
| At least five tests per core method | `AlgorithmsTest`, with exact small-instance and sorted-reference oracles. |
| At least three benchmark sizes | Evidence endpoint and JSON exports ([VALIDATION.md](VALIDATION.md)). |
| Baseline comparison | Trie versus scan, Quickselect versus sort, set cover versus first-useful selection. |
| Realistic data | Original lessons and problems, licensed external question metadata, live contest schedules, real learner actions, labelled synthetic benchmark generators. |
| Runnable source and documentation | Maven/npm, SQL migrations, import and content scripts, README, API docs. |
| Individual contribution/viva | Team must record actual names/IDs/contributions; review commit history and explain critical Java methods. |

## Viva preparation

Explain why an algorithm belongs in the product, not only its pseudocode. Be ready to change a test input and reason about the result. For Quickselect, distinguish expected and worst-case time; for set cover, distinguish correctness of coverage from exact minimum size; for trie, separate index construction from bounded query/output work. Explain where the frontend renders state and where Java computes it. Know how a hidden judge case is protected and why a Bloom-filter lesson describes positives as uncertain.

For the later services: explain why a drill can be graded without storing its answer (seeded regeneration); how one board renderer draws all sixteen new traces; how the contest cache avoids making requests wait on a slow site; why unrated bank questions sort last in both directions; and why the playground caps each tier at 95% utilisation.
