# Prep: aptitude, reasoning, puzzles, CS fundamentals and system design — design

## Intent

After seeing DSABuddy's Learn menu, the owner asked for "all these" alongside 1on1's DSA lessons:
- Aptitude
- Reasoning
- Puzzles
- CS fundamentals (OOP, DBMS, OS, networks, SQL)
- System design with a traffic playground

The aim is placement-prep breadth. Depth: the **core set** (my recommendation, accepted with "yes do it all"). It can
be extended later in the same format. All content is original. Nothing is copied from DSABuddy or any other site.

## Goals

- **A new area, "Prep"** at `/prep`, in the sidebar after "Explore concepts", with five tracks:

  | Track | Content |
  | --- | --- |
  | Aptitude | 8 topic guides (formulas, shortcuts, two worked examples each) plus unlimited generated drills per topic |
  | Reasoning | 5 topic guides plus unlimited generated drills per topic |
  | Puzzles | 20 classic puzzles (public-domain ideas), each with two hints, a stepwise solution and, where it has one, a checkable answer |
  | CS fundamentals | 5 subjects × 6 guides = 30 guides, each with sections and a 5-question graded quiz |
  | System design | 8 guides with 5-question quizzes, plus the traffic playground |

- **Aptitude topics:** percentages; profit and loss; ratio and proportion; averages; simple and compound interest; time
  and work; speed, distance and time; number systems (divisibility, LCM and HCF).
- **Reasoning topics:** number series; letter series; coding–decoding (letter shift); direction sense; syllogisms
  (two-premise templates).
- **Quizzes and drills feed the existing evidence.** Quiz attempts are stored as challenge attempts and shown as
  per-track progress on `/prep` (my call). Drill answers log a daily practice event (my call). Neither is added to the
  DSA concept map, its review or the `/progress` lesson count.
- **The playground:** a learner configures a tiny system, sees what happens, and changes it.
  - Settings: request rate, number of app servers behind a load balancer, cache on or off with a hit-rate slider,
    database capacity.
  - Results: throughput, latency, dropped requests and the bottleneck.

## Non-goals and anti-goals

- **No copying** DSABuddy's or anyone's notes, questions or puzzles. Classic puzzles are written fresh.
- **No change to the DSA lessons,** the concept map, the 24/33 counts, or their review schedule.
- **No claim of exam or company coverage.**
- **The playground is a teaching model, not a capacity planner.** It says so on the page.

## Approaches

| Approach | Trade-off | Chosen |
| --- | --- | --- |
| A separate Prep area with a "guide" content kind; quizzes graded by the existing challenge engine; aptitude and reasoning generated on the server; the playground simulated in the browser | New page components, but the DSA curriculum is untouched and the grading machinery is reused | **Yes** |
| Store everything as lessons in the DSA library | Least code, but it pollutes the concept map, prerequisite order and review, and breaks the curriculum tests | No |
| Plain reading pages without quizzes | Fastest, but no grading, progress or review | No |

## Design

### Content

- **Format:** a generator module (`scripts/prep_content.py`, invoked by `generate_content.py`) writes a new resource,
  `backend/src/main/resources/prep.json`:

  ```
  {tracks:[{id,title,summary,order}],
   guides:[{id:"guide-<track>-<slug>", track, title, order, summary,
            sections:[{title,text}], keyPoints:[str], quiz:[challenge…],
            drill?: topicId, puzzle?: {statement, hints[2], solution[steps], answer?}}]}
  ```

- **Authoring:** guide text and quizzes are authored in `scripts/prep/<track>_batch_*.py` files and checked by
  `scripts/prep/check_prep.py`. The checks:
  - section length and count;
  - exactly 5 quiz questions, each a valid `prediction`-kind multiple-choice challenge with 3–4 options, an in-range
    answer, an explanation and a hint;
  - unique ids;
  - no empty fields.

  Drafting happens in subagent batches, as with the lesson prose. Every claim is the author's own writing.
- **Loading:** `ContentSeed` stores each guide as a `guide` document, owner `public`. A document flagged `edited` is
  not overwritten, as for lessons. An admin editor for guides is out of scope (my call). Guides change by
  regenerating content.
- **Correctness review (my call):** `check_prep.py` checks structure only. Each authored batch also gets a separate
  fact-check pass by a second reviewer, which checks every quiz answer and explanation against the guide text, before
  it is merged.

### Grading

- `ChallengeService.find` also searches published `guide` documents, so `POST /challenges/{id}/attempts` grades guide
  quizzes unchanged. Attempts record the guide id in `lesson_id`.
- **Progress (my call):** the `/prep` track cards and each track's guide list show "quiz passed" per guide and
  "x of y guides passed" per track. They are computed in the browser from the `attempts` the progress summary already
  returns. A guide counts as passed when all 5 of its quiz questions have a correct attempt. No new endpoint, and the
  `/progress` page and its lesson counts are unchanged.
- **No spaced review for Prep (my call).** Review stays for the 24 DSA concepts. Prep quizzes can be retaken any time.
  "Review" in the rejected approach meant being able to revisit and re-grade, which guides allow.
- `LearningMapService` and `PlanService` only consider DSA lesson ids, so they ignore guide attempts.

### Generated drills

`DrillService` serves the aptitude and reasoning drills.
- `GET /api/v1/drills/{topic}/next?seed=` returns `{topic, seed, prompt, options?, unit?}`. The seed is random when
  absent.
- `POST /api/v1/drills/{topic}/answer {seed, answer}` returns `{correct, expected, explanation}`.
- The server regenerates the question from `(topic, seed)` to grade it, so the answer never reaches the client before
  the learner submits.
- Each generator is a pure function `(seed) -> {prompt, answer, explanation, options?}` with integer or exactly
  rounded answers. Numeric answers match exactly after trimming; series answers match exactly.
- **Recording (my call):** a signed-in answer calls `progress.record(user, "drill", topic)`, one learning event per
  topic per day, so drills appear on the activity heatmap. No attempt rows are written, so unlimited drilling never
  inflates the progress payload. The session streak lives in the browser. Drills are public, like lessons.

### Puzzles

Each puzzle is a guide with a `puzzle` block and no quiz. The page reveals hint 1, then hint 2, then the solution.
- **Checking (my call):** when `answer` is set, an answer box posts to `POST /api/v1/prep/puzzles/{id}/check
  {answer}` and gets back `{correct}`. Matching trims and ignores case, and the answer is not sent to the client
  first.
- **Recording:** a signed-in correct answer logs `progress.record(user, "puzzle", id)`.
- `ChallengeCard` is unchanged. `check_prep.py` requires 5 quiz questions for guides and 0 for puzzles.

### Pages

- **Routes:** `/prep` (the five track cards), `/prep/:track` (the guide list plus a drill entry for aptitude and
  reasoning), `/prep/guide/:id` (a guide or a puzzle) and `/prep/system-design/playground`.
- **Guide page:** a textbook layout (the existing tokens and `.prose`), a list of key points, then the quiz using the
  existing `ChallengeCard`.
- **Drill page:** one question at a time, an answer field or options, Check, the explanation, Next, and a session
  streak counter kept in the browser.

### The playground

- A pure TypeScript model in `src/pages/prep/trafficModel.ts`:
  - App servers are M/M/c queues with a per-server service rate.
  - The database is an M/M/1 queue that sees only cache misses.
  - Load above capacity becomes dropped requests.
- It reports throughput, the average latency (mean response time, exact for these queue models), utilisation per tier, drops and the bottleneck tier. Values are
  clamped and documented.
- Unit tests pin the model's monotonic behaviour and specific values.
- The UI is sliders with a live diagram (client → load balancer → servers → cache → database) whose tiers colour by
  utilisation, plus a "what changed" sentence.

## Constraints

- Additive only: no schema change (attempts reuse `challenge_attempts`), no change to the DSA content counts.
- Textbook UI tokens; accessible sliders, quizzes and drills; works at 390 px.
- Content is original and checked by `check_prep.py` before it is merged.

## Order of work

1. The Prep area, the guide format, quiz grading, and CS fundamentals (the largest content).
2. Aptitude and reasoning (generators plus their guides).
3. Puzzles.
4. System design guides and the playground.

## Left to the builder

- Exact section counts per guide (3–5) and per-guide wording.
- Which classic puzzles to include.
- The playground's default numbers and diagram styling.
- The streak counter's look.
