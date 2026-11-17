# Phase 2 handoff — 16 November 2026

**Delivered on the local `phase2` branch:** the four Phase 2 blocks in [the approved plan](IMPLEMENTATION_PLAN.md):
the full catalogue, the guided coding coach and Blob, dashboard, planning and review, and the document notebook. Also
delivered: admin publication checks and a content-authoring guide. Nothing has been pushed or deployed.

**Open gates.** Phase 2 must not be presented as fully accepted until these pass:

1. **Live execution (Judge0 under Docker).** Unchanged from [Phase 1](PHASE1_HANDOFF.md#exact-runner-blocker). The
   coach's journey from an actual failing run to a learner correction to an accepted submission has been tested with
   runs recorded the way the runner records them, not with a live sandbox.
2. **Live Gemini.** No key is configured on this machine. The Blob's graduated levels, the coach context and the
   notebook's cited answers are tested up to the provider boundary. In the browser, the answering states were checked
   with a reply stubbed inside the page.
3. **C++ references.** 52 problems have none, and the 8 that exist are unverified, because there is no local compiler or
   Judge0. Learners using C++ see the Java reference with a note saying so.
4. **Admin editor in a browser.** No local administrator account is configured, so the editor UI has only been
   type-checked. Its server checks are covered by `AdminChecksTest`.

## What changed

| Block | What a learner or editor gets | Main code |
| --- | --- | --- |
| Dashboard, planning, review | Concept map (24 concepts, prerequisite order) with an accessible list. Evidence states: explored, passed, accepted. A next action. Spaced review at 1/3/7 days; a miss returns tomorrow; a hinted success repeats its interval. Dated plan tasks with completion, rescheduling and regeneration that keeps finished work. Reviews link to the missed challenge and the learner's notes. | `LearningMapService`, `ReviewSchedule`, `PlanService`, `V3__review_evidence.sql`, `pages/LearningMap.tsx`, `workspace/Planner.tsx` |
| Document notebook | Text PDFs up to 10 MB / 100 pages. Extraction keeps page numbers (PDFBox). Search is Lucene BM25 over the learner's own selected sources only. Answers carry file and page citations and say when the sources don't answer. Revision cards are editable, with self-reported recall kept apart from graded results. Scanned, protected, oversized and non-PDF files are refused with a reason. | `NotebookService`, `NotebookController`, `V4__document_notebook.sql`, `workspace/DocumentNotebook.tsx` |
| Catalogue: lessons | All 24 core lessons, plus Quicksort, have at least two substantive challenges, a pattern drill, a dry run graded against the real trace, and linked problems. The 22 thin lessons have a new opening, a worked example that follows the animation's own trace, an invariant section, a cost section and reasons for each prerequisite. Code sections now match their animations; Quicksort had been showing merge code. | `scripts/practice_content.py`, `scripts/lesson_content.py`, `scripts/lesson_prose/`, `scripts/curriculum_content.py` |
| Catalogue: problems | All 60 problems have a Python reference verified on every fixture, three problem-specific hints, a full editorial, and two hidden adversarial cases agreed by the Java and Python references. | `scripts/problem_content.py`, `scripts/problem_batches/` |
| Coding coach | A Coach tab per problem: plan (approach, invariant, worked example) → code → run → fix → reflect. Nudges come one at a time, built from the learner's own plan and actual run results; edited code marks old runs as stale. The worked solution needs an explicit confirm, then comes with a transfer question. The coach never writes credit. | `CoachService`, `CoachController`, `components/CoachPanel.tsx` |
| Blob | Posture shows its state (idle, thinking, answered, error, AI unavailable) with reduced-motion support. Suggestions fit the lesson step or the problem. A four-level "still stuck" ladder. An offline notice before typing. The coach's plan, hints and run evidence go to the model (no hidden inputs, no solution code). | `TutorService` (`level`, coach context), `components/Tutor.tsx`, `components/BlobMark.tsx` |
| Practice hub | Question bank of 12,800+ external questions (Codeforces API; LeetCode via an MIT company dataset; metadata and links only) beside 1on1's own problems, 187 community-reported company lists, and timed mock assessments scored from official accepted runs. | `scripts/import_questions.py`, `BankService`, `MockService`, `pages/practice/` |
| Prep | Five tracks: CS fundamentals (30 guides), aptitude (8) and reasoning (5) with unlimited server-generated drills, puzzles (20, hints then solution, typed answers checked on the server), and system design (8 guides plus a traffic playground). Every guide quiz is graded on the server; every content batch was fact-checked by a separate pass. | `PrepController`, `DrillService`, `scripts/prep/`, `pages/prep/` |
| Sheets and sources | Blind 75 and NeetCode 150 sheets (MIT data) with ticks, "solve here" and a link to the teaching lesson; the bank adds AtCoder and CSES (16,331 questions). Striver lists are linked only; no licensed source of newer company tags exists. | `SheetController`, `scripts/import_questions.py`, `pages/practice/Sheets.tsx` |
| Contests and lab | Upcoming Codeforces and AtCoder contests in local time with calendar export; LeetCode sync ticks sheet questions; bank sorting; a Phase 3 performance lab comparing trace steps with growth curves. Also: a redesigned landing page, grouped navigation and a Ctrl+K command palette. | `ContestService`, `LabService`, `pages/contests/`, `pages/LabPage.tsx`, `components/CommandPalette.tsx` |
| Explore extras | Every animation on one page (`/learn/animations`, loaded on demand); the 7 advanced lessons now have full prose, objectives and four practice questions each, fact-checked against their traces. | `pages/Animations.tsx`, `scripts/lesson_prose/batch_3.py` |
| Textbook UI | Paper and night themes, Fraunces/Source Serif 4/Inter Tight, six algorithm-family colours (library groups, map dots, lesson and problem headers, trace highlights), editor themes. Design and plan in `docs/superpowers/`. | `src/families.ts`, `components/FamilyMark.tsx`, `components/editorTheme.ts`, `src/styles.css` tokens |
| Admin | Check, preview, save draft, publish. Errors block saving; publication checks block publishing; references are never executed in the editor. | `ContentChecks`, `AdminController`, `workspace/Admin.tsx` |

API changes are in [API.md](API.md). How to write and check content is in [CONTENT_AUTHORING.md](CONTENT_AUTHORING.md).
Migrations V3 and V4 are additive; no applied migration was edited and no learner database needs a reset.

## Setup notes added in Phase 2

- **Admin account:** set `ADMIN_EMAIL` and `ADMIN_PASSWORD` (12+ characters) in your local `.env` before starting the
  backend; the account is created on startup.
- **Browser tests:** `npm run test:e2e` needs the Chromium build matching the installed Playwright. On this machine it
  expects build 1255 while 1243 and 1248 are installed. Either run `npx playwright install chromium`, or point a local,
  uncommitted config at an installed headless shell through `launchOptions.executablePath`.
- **After regenerating content:** restart the backend so `ContentSeed` reloads it. Records an administrator saved are
  kept.

## Observed verification

Observed on Windows 11, Java 25 (release 21), Node 22, Python 3.13, on 16 November 2026.

| Check | Result |
| --- | --- |
| `npm run verify` | **Backend:** 97 tests pass, including the ones below. **Frontend:** 9 tests pass. **Production build** succeeds. |
| Backend tests covering Phase 2 | `ContentTest` runs every Java reference on all 546 fixtures. `CurriculumTest` compiles every teaching example and lesson override and runs their cases. Other suites: `PracticeContentTest`, `CoachTest`, `PlanAndMapTest`, `ReviewScheduleTest`, `NotebookTest`, `AdminChecksTest`, `TutorLevelsTest`. |
| `python scripts/verify-references.py` | Python passes every fixture for all 60 problems. C++: 52 missing, 8 not verified (no compiler). |
| Problem batch checker | 52 of 52 problems pass. Java and Python agree on all 104 new cases. |
| Lesson prose checker | 22 of 22 lessons pass. Every number in a worked example appears in that lesson's trace. |
| Browser suite, first full run | 47 of 51 passed. The 4 failures led to the fixes below. |
| Browser re-runs after the fixes | Passed: the guest journey (library list), curriculum code sections, tutor history scoping, and the new 33-lesson catalogue sweep at alternating desktop and phone widths. The custom-input fix was confirmed with a scripted run of the same steps, not by re-running that spec. |
| Not re-run | The full 51-test suite after the last fixes was stopped at the owner's request. Run `npm run test:e2e` before release. The 60-problem sweep now reloads a page once if the Vite dev proxy drops its editorial request, and records it as `retried`. |

Earlier in Phase 2 these were checked by hand in the browser:
- the concept map, plan task completion, and re-planning;
- PDF upload with cited answers, revision cards, and source deletion;
- each block's lesson pages, the problem Coach tab, and the Blob's offline and answering states (the answering states
  with a stubbed reply).

## Found and fixed by the exit gate

- **Library list hidden on desktop:** the concept map's phone list reused the class `concept-list`, which hid the
  library's lesson list on desktop. The guest journey test caught it, and the map list now has its own class.
- **Quicksort:** it shared the sorting concept's merge code, example and complexity, and had no practice challenges or
  linked problems. It now has its own tested code section, drills and linked problems.
- **Code sections that disagreed with their animations:** hashing, variable window, backtracking, merge sort,
  memoization, and the DFS start text.
- **Tabulation** had no prerequisite reasons.
- **Experiment edits wiped on a fresh lesson load:** typing into an experiment right after a lesson opened could be
  reset to the default input. The Blob's first system-status request was remounting the lesson. Status is now fetched
  once in the app shell, so the Blob only reads it. The lesson page also seeds its experiment from the saved position
  only when a lesson opens, so later saves can't overwrite what the learner is editing.
- **Two browser tests updated to the new behaviour:** Merge Sort's code section now shows the full sort, and a
  lesson's tutor suggestions name that lesson's challenge.

## Remaining backlog

1. **Close the runner gate,** then run `npm run verify:live` and perform the coach journey with real runs in all three
   languages. Include a compile error, a timeout and a runner outage.
2. **Add a Gemini key locally** and check:
   - each help level's answers stay within its bound;
   - the coach context produces grounded, hypothesis-labelled feedback;
   - notebook answers cite the right pages.
3. **Add and verify C++ references,** using the existing problem batch checker pattern with a C++ runner.
4. **Check the admin editor in a browser** with a local admin account: check, preview, draft, publish, and a deliberate
   error.
5. **Minor content:**
   - The Graphs trace keeps its array at -1 throughout.
   - Several traces label the input length `size` at step 0.
   - The backtracking animation stops at five values.
   - Nine advanced lessons (AVL, Dijkstra and others) still have the older, thinner prose; Phase 2 required only the 24
     core lessons.
6. **Phase 3:** own-code tracing, profiling, MCP and external skills, as planned.

## Attribution

This branch was built with substantial AI assistance (Claude), and its commits carry a Co-Authored-By trailer. Incoming
teammates should read and understand each module before extending it, record their own contributions, and not present
this work as independently authored student code.
