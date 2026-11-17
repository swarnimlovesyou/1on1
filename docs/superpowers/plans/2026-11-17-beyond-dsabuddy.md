# Beyond DSABuddy and completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Close the remaining gaps against DSABuddy (contests, profile-synced sheets, bank sorting), clear the deferred review items, add Phase 3's performance laboratory, and run the full regression the exit gate asks for.

**Architecture:** A `ContestService` reads the Codeforces official `contest.list` and AtCoder Problems' `contests.json`, cached for an hour; LeetCode and CodeChef are linked, not scraped or guessed. The existing LeetCode connection's recent accepted submissions tick matching sheet items. The bank gains a `sort` parameter. The performance lab counts the steps of the existing Java traces over growing inputs.

**Tech Stack:** Spring Boot 4 / Java 21 (`RestClient`), React + react-query, Vitest, Playwright.

**Spec:** the owner's request on 2026-11-17 ("work on features which are left to get better than DSABuddy and whatever is needed to complete"), the DSABuddy comparison from the source research, `docs/IMPLEMENTATION_PLAN.md` § Phase 3, and `docs/PHASE2_HANDOFF.md` next steps.

## Global Constraints

- Only official APIs or openly licensed data; no scraping of LeetCode, CodeChef or DSABuddy, and no guessed schedules shown as fact.
- External calls are cached and degrade honestly ("couldn't reach Codeforces; showing the last list from …").
- Additive only; no schema migration is needed (documents in the existing store).
- Accessible, works at 390 px, both themes.

## Review Focus

1. **A contest source is down or slow:** the page still renders the other source and says which one failed. Pinned in Task 1.
2. **Time zones:** start times render in the learner's local zone; the .ics file uses UTC. Pinned in Task 1.
3. **A LeetCode sync that returns slugs on no sheet, or none at all:** no ticks change, nothing errors. Pinned in Task 2.
4. **Sorting with filters and paging:** stable order across pages; unrated questions last. Pinned in Task 3.
5. **Performance lab inputs at the largest size:** bounded time, no trace over the existing step cap. Pinned in Task 5.

---

### Task 1: Contests
- `ContestService.upcoming()` → `{contests:[{id, platform, title, start (ISO UTC), durationMinutes, url}], sources:[{platform, ok, fetchedAt}]}`; Codeforces `contest.list?gym=false` (phase BEFORE/CODING), AtCoder contests with `start_epoch_second` in the future; cache 60 min; a failed source keeps its last good list and reports `ok:false`.
- `GET /api/v1/contests` (public). `ContestTest` with a stubbed fetcher: merge and sort by start, a failing source, cache reuse.
- `/contests` page (sidebar under Practise): grouped by day in local time, countdown, duration, platform filter, "Add to calendar" (.ics built in the browser), links to LeetCode and CodeChef contest pages. Vitest for the .ics builder; `tests/contests.spec.ts` with a mocked API.

### Task 2: Sheets tick from the LeetCode connection
- On a successful sync, `recentAcSubmissionList` slugs that match a sheet item (`lc-<slug>`) are added to the learner's ticks; the response says how many. `SheetTest`/`LeetcodeSyncTest` pins: matches tick, non-sheet slugs ignored, empty list is a no-op, existing ticks kept.
- The sheets view says "Ticks also update when you sync LeetCode (last 20 accepted)".

### Task 3: Bank sorting
- `sort` = `relevance` (default) | `easiest` | `hardest` | `title` | `reported` (company only). Rating order uses Codeforces/AtCoder rating, then Easy/Medium/Hard; unrated last; ties by id. `BankTest` pins order and paging stability. A sort select in the bank, kept in the URL.

### Task 4: Deferred review items
- Drill page: no full-page spinner on Next, Next disabled while checking, state keyed by topic, syllogism prompt on separate lines, "15%" without a space.
- Playground: "Dropped …/s", `aria-live` only on the change sentence; spec wording updated to "average latency".
- Gallery, sheets: control names include the item title. Sheets: malformed stored ticks ignored. AtCoder rating floor 1.

### Task 5: Performance laboratory (Phase 3)
- `GET /api/v1/lab/{algorithm}?sizes=8,16,…` → step counts of the existing Java traces for random inputs of each size (≤ 256, seeded), with reference curves n, n log n, n². Supported: binary search, merge sort, quicksort, sliding window, two pointers, prefix sums.
- `/learn/lab` page: chart of measured steps against the curves, honest note that steps are the trace's operations, not wall-clock time.

### Task 6: Verify and document
- Full `npm run verify` and the full Playwright suite (every spec), docs (`API.md`, `PHASE2_HANDOFF.md`, `FEATURES.md`), one final review, one fix pass.

Not in scope here: own-code tracing (needs the isolated runner, which isn't available on this machine), the MCP adapter, and the PostgreSQL rehearsal (needs the owner's database credentials).
