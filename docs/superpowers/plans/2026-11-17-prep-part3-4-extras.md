# Prep parts 3–4 and extras Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Puzzles (20), system design (8 guides + traffic playground), an animations gallery, deeper advanced lessons, and — once their reuse terms are confirmed — curated-list sheets and fresher company data.

**Architecture:** Puzzles are guides with a `puzzle` block, checked by `POST /api/v1/prep/puzzles/{id}/check` (reusing `DrillService.matches`). System design guides use the existing guide format; the playground is a pure TypeScript queueing model (`trafficModel.ts`) behind a slider page. The gallery reuses each lesson's existing `Experiment`. Advanced lessons gain prose and practice through the existing `lesson_prose` and `practice_content` pipelines.

**Tech Stack:** Spring Boot 4 / Java 21, React + react-query, Vitest, Playwright, Python content scripts.

**Spec:** `docs/superpowers/specs/2026-11-17-prep-design.md` (Puzzles, The playground, Pages). Extras were requested by the owner on 2026-11-17 ("do it all asap") after the Explore audit and the Ladder comparison.

## Global Constraints

- Additive only; the 24 concepts and their review are unchanged; advanced lessons stay outside the concept map.
- Puzzle answers never reach the client first; matching trims, ignores case, compares numbers by value.
- A signed-in correct puzzle answer calls `progress.record(user, "puzzle", id)`.
- The playground says it is a teaching model, not a capacity planner.
- All content original, structure-checked, then fact-checked by a separate pass. Curated lists and new datasets are imported only after their licence/terms are confirmed; titles and links only.
- Textbook UI tokens; accessible controls; works at 390 px.

## Review Focus

1. **A puzzle answer typed as " 17 ", "Seventeen" or "17." :** trimmed/case-insensitive/numeric match; the word form is wrong (documented). Pinned in Task 1.
2. **Checking a puzzle without an answer, a non-puzzle guide, or an unknown id:** 400/404 with a sentence. Pinned in Task 1.
3. **Playground extremes (0 servers impossible; rate 0; hit rate 100%; load far above capacity):** finite numbers, no NaN/Infinity on screen. Pinned in Task 2.
4. **Hints and solution revealed in order:** hint 2 not shown before hint 1; solution last. Pinned in Task 1.
5. **Gallery with 33 animations:** loads without 33 simultaneous trace requests; works at 390 px. Pinned in Task 3.

---

### Task 1: Puzzles
- Checker: a guide with `puzzle` needs `statement`, exactly 2 `hints`, ≥ 2 `solution` steps, optional non-empty `answer`, `sections == []`, 1–3 keyPoints, 0 challenges; `track == 'puzzles'` requires a puzzle. Tests first in `test_check_prep.py`.
- `PrepController.check(user, id, {answer})` → `{correct}`; unknown/non-puzzle → 404 "That puzzle doesn't exist."; no answer → 400 "This puzzle has no single answer to check."; blank → 400. Tests in `PrepTest`.
- Guide page: statement; "Show a hint" reveals hint 1 then hint 2; "Show the solution" last; answer box when `checkable`. `tests/puzzles.spec.ts`.
- Content: `scripts/prep/puzzles_batch.py` (writer + fact-check).

### Task 2: System design and playground
- `src/pages/prep/trafficModel.ts`: `simulate({rate, servers, serviceRate, cache, hitRate, dbCapacity}) → {throughput, dropped, latencyMs, appUtil, dbUtil, bottleneck}`; app tier M/M/c (Erlang C), database M/M/1 on cache misses, admitted load capped at 95% of capacity, the rest dropped. Unit tests pin M/M/1 (λ=50, μ=100 → 20 ms), M/M/c (c=2, μ=100, λ=100 → 13.33 ms), monotonicity and extremes.
- `PlaygroundPage.tsx` at `/prep/system-design/playground`, linked from the track; sliders, tier diagram coloured by utilisation, a "what changed" sentence, the disclaimer. Spec in `tests/playground.spec.ts`.
- Content: `scripts/prep/system_design_batch.py` (writer + fact-check).

### Task 3: Animations gallery
- `/learn/animations`: every lesson's animation, grouped by family, each mounted on demand ("Play this animation") so the page never fires 33 traces at once. Linked from the library. Spec in `tests/gallery.spec.ts`.

### Task 4: Advanced lessons
- `lesson_prose/batch_3.py` and `PRACTICE` entries for avl, trie, dijkstra, max-flow, set-cover, quickselect, bloom-filter; tests updated to the new counts plus an advanced-lesson assertion.

### Task 5: Curated lists and company data (gated)
- Only sources the research marks reusable. Lists become Practice sheets: each question links out, opens in "solve here", can be ticked, and points to the 1on1 lesson that teaches it.

### Task 6: Verify, document, review
- `npm run verify`, all Prep specs, docs (`API.md`, `PHASE2_HANDOFF.md`), one fresh final review, one fix pass.
