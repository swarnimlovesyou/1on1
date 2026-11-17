# Practice Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a question bank of external questions (about 11,000), company lists and timed mock online assessments to
Practice.

**Architecture:**
- A Python import script writes `external-questions.json` from Codeforces' official API and an MIT LeetCode company
  dataset.
- A Java `BankService` serves it, filtered and paged, together with 1on1's own problems.
- A Java `MockService` stores timed attempts as `mock` documents in `Store`, scoring them from existing official
  submissions.
- The React Practice page gains four tabs.

**Tech Stack:** Python 3 (stdlib only), Spring Boot 4 on Java 21, JdbcTemplate `Store`, React, react-query and Vitest.

**Spec:** `docs/superpowers/specs/2026-11-17-practice-hub-design.md`

## Global Constraints

- **Metadata only:** id, source, title, url, difficulty, tags, rating and companies. Never problem statements.
- **Sources:**
  - Codeforces `https://codeforces.com/api/problemset.problems`, credited "Codeforces".
  - `hxu296/leetcode-company-wise-problems-2022` files `data/leetcode_problems.csv` and
    `data/companies_and_leetcode_problems.csv`, MIT © 2022 Huan Xu, credited on the bank and companies pages.
- **Codeforces difficulty:** below 1300 is `Easy`, 1300–1899 is `Medium`, 1900 and above is `Hard`, and an unrated
  problem has none.
- **Company label, verbatim:** "Community-reported (LeetCode company tags, 2022 snapshot)". Never "asked at".
- **No requests to LeetCode or DSABuddy.** External questions open the original site in a new tab and are never judged
  in-app.
- **Mock OA:**
  - 2 or 3 problems, 60 or 90 minutes.
  - The server enforces the deadline.
  - Only official ACCEPTED submissions created inside the window count.
  - The mock never writes credit.
  - Integrity signals are counts reported by the client: tab switches and fullscreen exits.
- **No schema change.** The textbook UI tokens and `FamilyMark` apply.

## Review Focus

1. **A deadline passed while the browser was closed:** reopening shows the attempt as finished, scored only from
   submissions made before the deadline. Pinned in Task 3.
2. **A submission made after the deadline or before the start, or a custom (unofficial) run:** never counted. Pinned in
   Task 3.
3. **Another learner's mock id:** returns 404 and leaks nothing. Pinned in Task 3.
4. **A bank query with no matches, or a page past the end:** returns an empty `items` list with the correct total, not
   an error. Pinned in Task 2.
5. **A company whose list has no Hard problems, in company style:** the mock still picks the requested number of
   problems, filling from neighbouring difficulties. Pinned in Task 3.

---

### Task 1: Import external questions

**Files:**
- Create: `scripts/import_questions.py`
- Create (generated, committed): `backend/src/main/resources/external-questions.json`
- Test: `scripts/test_import_questions.py` (stdlib `unittest`)

**Interfaces:**
- Produces a JSON list of records with this shape:

  ```
  {"id": "cf-1520A" | "lc-two-sum", "source": "Codeforces" | "LeetCode", "title": str, "url": str,
   "difficulty": "Easy" | "Medium" | "Hard" | null, "tags": [str], "rating": int | null,
   "companies": {name: count}}
  ```

- Pure functions in the script:
  - `cf_difficulty(rating: int | None) -> str | None`
  - `cf_record(p: dict) -> dict`
  - `lc_records(problems_csv: str, companies_csv: str) -> list[dict]` (both arguments are CSV text)

- [ ] **Step 1: Write the failing tests.**
  - `cf_difficulty`:
    - `cf_difficulty(None) is None`
    - `cf_difficulty(800) == "Easy"`
    - `cf_difficulty(1299) == "Easy"`
    - `cf_difficulty(1300) == "Medium"`
    - `cf_difficulty(1899) == "Medium"`
    - `cf_difficulty(1900) == "Hard"`
  - `cf_record({"contestId":1520,"index":"A","name":"Do Not Be Distracted!","rating":800,"tags":["brute force"]})`
    returns:
    - `id` `"cf-1520A"`
    - `url` `"https://codeforces.com/problemset/problem/1520/A"`
    - `difficulty` `"Easy"`
    - `tags` `["brute force"]`
    - `companies` `{}`
  - `lc_records` on a two-row problems CSV (whose `difficulty` has trailing spaces) and a companies CSV mapping both to
    Google, one also to Amazon:
    - the id is the slug from the link, prefixed `lc-`;
    - difficulty is stripped;
    - `companies == {"Google": 3, "Amazon": 1}`, with counts parsed as integers.

- [ ] **Step 2: Run** `python -m unittest scripts/test_import_questions.py`. Expected: FAIL (ImportError).

- [ ] **Step 3: Implement the three functions and `main()`.**
  - `main()` fetches the three URLs with `urllib.request`, using a plain User-Agent and a 60 s timeout.
  - Before writing the CSV columns, read the header of `companies_and_leetcode_problems.csv` and use its actual column
    names.
  - Write the file sorted by `(source, id)` with `ensure_ascii=False`, and print the counts per source.

- [ ] **Step 4: Run the tests again.** Expected: PASS. Then run `python scripts/import_questions.py`.
  Expected: about 10,000 Codeforces and 1,338 LeetCode records, and a file under 5 MB.

- [ ] **Step 5: Commit** with the message "Import external question metadata from Codeforces and an MIT LeetCode company
  dataset".

### Task 2: Bank API

**Files:**
- Create: `backend/src/main/java/com/oneonone/BankService.java`
- Create: `backend/src/main/java/com/oneonone/BankController.java`
- Modify: `SecurityConfig` (permit `GET /api/v1/bank/**`, as other public content is)
- Test: `backend/src/test/java/com/oneonone/BankTest.java`

**Interfaces:**
- Consumes `external-questions.json` (Task 1), plus 1on1 problems from `store.list("problem","public")` that are
  published.
- `BankService` methods:
  - `Map<String,Object> search(String q, String source, String difficulty, String topic, String company, int page, int size)`
    returns `{items, total, page, size}`.
    - 1on1 rows come first, with `source` "1on1", `url` "/practice/<id>", tags equal to their topics, and empty
      companies.
    - The filters are case-insensitive. `q` matches a substring of the title. `topic` must equal a tag, ignoring case.
      `company` must be a key in companies.
    - With a company filter, rows are sorted by that company's count, descending.
    - `size` is clamped to 1–100.
  - `List<Map<String,Object>> companies()` returns `[{name, count}]`, sorted by count descending.
  - `Map<String,Long> difficultyMix(String company)` counts the company's questions per difficulty. Task 3 uses it.
- Endpoints, both with no auth: `GET /api/v1/bank?q&source&difficulty&topic&company&page=0&size=25` and
  `GET /api/v1/bank/companies`.

- [ ] **Step 1: Write the failing `BankTest`.** Build `Store` on H2 the way `PlanAndMapTest` does, and load
  `content.json` problems. Assert:
  - An unfiltered search has `total >= 11000`, and its first item has source `1on1`.
  - Filtering by source `Codeforces` and difficulty `Hard` returns only Codeforces Hard rows.
  - Filtering by `company=Google` returns only rows that have a Google count, and the counts are non-increasing.
  - Searching for `q=zzzz-no-such-title` gives `total == 0` and an empty `items`. Page 9999 also gives an empty
    `items`.
  - `companies()` is non-empty, and Google's count is greater than 0.
  - `size` 1000 is clamped to 100.

- [ ] **Step 2: Run** `mvn -q test -Dtest=BankTest`. Expected: FAIL (compile error).

- [ ] **Step 3: Implement.** Load and cache the JSON once, lazily, with `store.json`. Filter with plain streams.

- [ ] **Step 4: Run the test again.** Expected: PASS.

- [ ] **Step 5: Commit** with the message "Serve a filterable question bank with company lists".

### Task 3: Mock OA backend

**Files:**
- Create: `backend/src/main/java/com/oneonone/MockService.java`
- Create: `backend/src/main/java/com/oneonone/MockController.java` (authenticated)
- Test: `backend/src/test/java/com/oneonone/MockTest.java`

**Interfaces:**
- Consumes `BankService.difficultyMix(company)` and `store.list("submission", user)`. A submission has `problem`,
  `official`, `status` and `createdAt`.
- A mock is a `Store` document `mock-<uuid>`, kind `mock`, owned by the user:

  ```
  {problems:[ids], style, startedAt, deadline, finishedAt?, signals:{tabSwitches, fullscreenExits}}
  ```

- `MockService` methods:
  - `start(String user, int size, int minutes, String style)` validates its arguments: `size` must be 2 or 3, `minutes`
    60 or 90, and `style` either `"mixed"` or a company name from `companies()`.
  - `view(String user, String id)` returns `{id, problems:[{id,title,difficulty,accepted:boolean,acceptedAt?}], startedAt,
    deadline, finished:boolean, remainingSeconds, score, signals}`.
    - `finished` is true once `finishedAt` is set or now is past the deadline.
    - `score` counts accepted problems.
    - A problem counts as accepted only through an official ACCEPTED submission with
      `startedAt <= createdAt <= min(deadline, finishedAt)`.
  - `finish(String user, String id)` sets `finishedAt` if it isn't already set.
  - `signal(String user, String id, String kind)` increments `tabSwitches` or `fullscreenExits`, but only while the
    attempt is unfinished.
  - `list(String user)` lists the user's mocks, newest first, each as `view`.
- Problem choice:
  - `mixed` draws one Easy, one Medium and one Hard; with size 2, one Easy and one Medium.
  - A company style allocates `size` across difficulties in proportion to `difficultyMix`, with largest remainders.
  - When a difficulty runs out, the gap fills from the nearest other difficulty.
  - The draw is random among published 1on1 problems, without repeats.
- Endpoints:
  - `POST /api/v1/mocks` with `{size, minutes, style}`
  - `GET /api/v1/mocks`
  - `GET /api/v1/mocks/{id}`
  - `POST /api/v1/mocks/{id}/finish`
  - `POST /api/v1/mocks/{id}/signals` with `{kind}`

- [ ] **Step 1: Write the failing `MockTest`.** Insert submissions as `CoachTest` does. Assert:
  - `start` with size 3 and `mixed` gives three distinct problems with difficulties Easy, Medium and Hard.
  - Size 4 or 45 minutes is rejected.
  - An official ACCEPTED submission inside the window counts. These don't count:
    - one at `startedAt` minus 1 s;
    - one after the deadline;
    - an unofficial one;
    - a WRONG_ANSWER.
  - After `finish`, a later accepted submission doesn't count, and `signal` no longer increments.
  - With a deadline already in the past (set by editing the document), `view` reports `finished` and
    `remainingSeconds` 0.
  - Another user's `view` throws a 404 `ResponseStatusException`.
  - A company style whose mix has no Hard problems still returns `size` problems.
  - The `solved_credits` count stays 0 throughout.

- [ ] **Step 2: Run** `mvn -q test -Dtest=MockTest`. Expected: FAIL (compile error).

- [ ] **Step 3: Implement** `MockService` and `MockController` as above. `now` comes from `Instant.now()`, and tests
  move the window by editing the stored document.

- [ ] **Step 4: Run the test again.** Expected: PASS.

- [ ] **Step 5: Commit** with the message "Add timed mock assessments scored from official runs".

### Task 4: Practice hub frontend

**Files:**
- Modify: `src/pages/Practice.tsx`. `Practice` gains tabs: "Our problems" (the current table), "Question bank",
  "Companies" and "Mock OA". The selected tab sits in the `?tab=` query.
- Create: `src/pages/practice/QuestionBank.tsx` (search, source, difficulty and topic filters; company filter from
  `?company=`; paged table)
- Create: `src/pages/practice/Companies.tsx` (company list; clicking one opens the bank with `?company=`)
- Create: `src/pages/practice/MockOA.tsx` (start form, active attempt with a countdown, report, past attempts)
- Modify: `src/pages/Practice.tsx` `ProblemPage`: when `?mock=<id>` is present, show a banner with the remaining time
  and a link back
- Modify: `src/types.ts` (`BankItem`, `BankPage`, `MockView`), `src/styles.css`
- Test: `tests/practice-hub.spec.ts` (Playwright)

**Interfaces:**
- Consumes the Task 2 and Task 3 endpoints.
- External rows link with `target="_blank" rel="noopener noreferrer"`. 1on1 rows use a router `Link`.
- The bank and companies pages show the exact credit line: "Questions from Codeforces and LeetCode, metadata only.
  Company lists: community-reported (LeetCode company tags, 2022 snapshot), MIT © 2022 Huan Xu."
- `MockOA` reports `visibilitychange` (hidden) and `fullscreenchange` (exit) to `/signals` while the attempt is active.
  When the countdown reaches 0, it calls `/finish`.

- [ ] **Step 1: Write the failing Playwright spec.**
  - `/practice?tab=bank` shows rows. Filtering source Codeforces and difficulty Hard shows only those rows.
    `?company=Google` shows the credit line.
  - A signed-up user starts a mock (3 problems, 60 minutes) and sees a countdown and 3 problem links. Each link carries
    `?mock=`.
  - Opening one shows the banner.
  - "Finish now" shows the report, with a score of 0 of 3.

- [ ] **Step 2: Run** `npx playwright test -c .cache/pw-local.config.ts tests/practice-hub.spec.ts`. Expected: FAIL.

- [ ] **Step 3: Implement the pages,** reusing `Loading`, `ErrorState` and `FamilyMark` (family from
  `familyOfProblem(tags)`) and the existing table styles.

- [ ] **Step 4: Run the spec again.** Expected: PASS. Also run `npm test` and `npx tsc --noEmit -p .`, which must pass.

- [ ] **Step 5: Commit** with the message "Add question bank, companies and mock OA to Practice".

### Task 5: Docs and full verification

**Files:**
- Modify: `docs/API.md` (the bank and mock endpoints), `docs/PHASE2_HANDOFF.md` (one row, plus data credits)

- [ ] **Step 1:** Run `npm run verify`. Expected: backend, frontend and build all pass.
- [ ] **Step 2: Commit** with the message "Document the practice hub".
