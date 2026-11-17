# Demonstration and assessment evidence

> Refreshed 17 November 2026. Feature status: [FEATURES.md](FEATURES.md). Technical detail: [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md). Live Judge0 runs, live Gemini answers and own-code tracing are not available on the demo machine; the script shows those states honestly instead of skipping past them.

## Before the demo

- Run `npm run dev` (Vite on port 5173, API on 8080). Open `http://localhost:5173` in a fresh window.
- Create a student account in advance and use it for a few real actions (a lesson, a drill), so the progress page has activity. Do not seed fake activity.
- The machine needs internet for the contests page. If a source is down, the page says so; that is part of the demo.
- Keep a second tab open on `/learn/lab` in case the network is slow.

## Ten-to-twelve-minute flow

Times are cumulative. "Click" is what to do; "Say" is one or two lines.

### 1. Landing (0:00–0:45)

- **Click:** open `/`. Point at the framed photo hero and its Unsplash credit, then "Open your first notebook".
- **Say:** "1on1 joins a visual explanation, the code, practice and review in one place. Every algorithm state you will see is computed by Java, not drawn by hand."

### 2. Library and an animation (0:45–2:15)

- **Click:** sidebar → Learn → Explore concepts. Show the grouped sidebar (Learn / Practise / Your work). Press Ctrl+K (⌘+K on macOS), type "sliding", open Sliding Window.
- **Say:** "33 lessons: 24 core concepts, two child lessons and seven advanced ones. The palette jumps to any lesson, guide or sheet."
- **Click:** in the experiment, change the input (e.g. `4, 4, 4, 1`), then play, step back, scrub.
- **Say:** "The trace comes from the Java trace engine; the browser only renders it. The running-sum invariant holds at every step."
- **Click:** sidebar → Animations. Press play on one other animation (e.g. Merge Sort).
- **Say:** "Every animation is on this page and runs its trace only when you press play."

### 3. Lesson practice (2:15–3:45)

- **Click:** back in the Sliding Window lesson, answer a prediction question wrong, read the feedback, then answer correctly. Do the pattern drill and fill one dry-run field.
- **Say:** "Answers are graded on the server; the browser never receives the answer key. The dry run is checked against the real trace step, and the first wrong field is named."
- **Say:** "A miss here schedules a review for tomorrow; successes return after 1, 3 and 7 days."

### 4. Performance lab (3:45–4:45)

- **Click:** sidebar → Performance lab. Choose Binary search, then Merge sort.
- **Say:** "The lab runs the real trace on random inputs of 4, 8, 16 and 32 values and counts its steps. Binary search follows log n, merge sort n log n."
- **Say:** "These are step counts of our own traces at small sizes, not wall-clock timing and not a proof of Big-O. Profiling your own code needs the isolated runner, which is not available here."

### 5. Practice: sheets, bank, solve here (4:45–7:15)

- **Click:** sidebar → Sheets → Blind 75. Tick a question; point at its lesson link and its reporting companies.
- **Say:** "Blind 75 and NeetCode 150 come from an MIT-licensed list. Ticks are saved to the account; a LeetCode profile sync can tick questions from the last 20 accepted solves."
- **Click:** Practice → Question bank. Set Company to a large company, then Sort → Hardest first.
- **Say:** "16,331 questions from Codeforces, AtCoder, CSES and LeetCode metadata: titles and links only, never statements. Company tags are community-reported, as of May 2022; they show what people reported, not what a company asks."
- **Click:** on a Codeforces question, press "Solve here". Type a short program and custom input, press Run.
- **Say:** "The statement stays on Codeforces. Runs here use your own input and are never graded. On this machine the runner is not available, so you see that state instead of a fake result."

### 6. Contests (7:15–8:00)

- **Click:** sidebar → Contests. Filter by AtCoder, then "Add to calendar" on one contest.
- **Say:** "Upcoming Codeforces and AtCoder contests in local time, cached for an hour. If a site fails, the last good list stays and the page marks that source as unavailable. LeetCode and CodeChef are linked, not read."

### 7. Prep: drill, puzzle, playground (8:00–10:15)

- **Click:** sidebar → Prep → Aptitude → Percentages → "Practise with unlimited questions". Answer with a unit, such as `15%`. Then "Next question".
- **Say:** "Each question is generated on the server from a seed. To grade, the server regenerates it from the seed, so the answer is never sent first."
- **Click:** Prep → Puzzles → "Handshakes at a meetup". Show one hint, type an answer.
- **Say:** "Two hints, then the solution. Typed answers are checked on the server."
- **Click:** Prep → System design → Traffic playground. Raise "Requests per second" until the app tier is the bottleneck, raise "App servers", then turn on the cache and raise its hit rate.
- **Say:** "App servers are an M/M/c queue, the database an M/M/1 queue that sees only cache misses. It is a teaching model of why latency rises sharply near full load, not a capacity planner."

### 8. Progress (10:15–11:00)

- **Click:** sidebar → Your work → Progress.
- **Say:** "Notebooks explored, problems accepted here, streak and an activity heatmap. Autosaves and open tabs don't count. Problems accepted stays at zero on this machine because no live runner is available."

### 9. Close (11:00–11:45)

- **Say:** "Not shown because they are not built or need services we don't have here: own-code tracing and live grading need the Judge0 runner under Docker; live Blob answers need a Gemini key; the PostgreSQL rehearsal needs the owner's database. A read-only MCP adapter over the public API is in progress; account pairing for it is not built. Tests: `npm run verify` passes, with 149 backend and 40 frontend tests."

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

For the later services: explain why a drill can be graded without storing its answer (seeded regeneration); why the lab compares curves on log error and why four sizes up to 32 cannot prove a complexity class; how the contest cache avoids making requests wait on a slow site; why unrated bank questions sort last in both directions; and why the playground caps each tier at 95% utilisation.
