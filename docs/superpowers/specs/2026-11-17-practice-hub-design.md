# Practice hub: question bank, companies and mock OA — design (approved)

## Intent

Give 1on1 the practice breadth of question-bank sites: a large, filterable bank of external questions, company lists and
timed mock online assessments. The data is pulled from public sources, not written by hand. The owner approved the
approach in conversation on 17 November 2026.

## Goals

- **Question bank:** about 11,000 external questions, filterable by source, difficulty, topic and company, alongside
  1on1's own 60 problems. External questions link to the original site.
- **Companies:** 187 company lists of LeetCode questions with how often each was reported. Every list is labelled as
  community-reported.
- **Mock OA:** a timed assessment of 2–3 of 1on1's own judged problems. The server enforces the deadline, scores
  accepted official runs, and records tab switches and fullscreen exits as integrity signals.
- **Solve in browser:** unchanged. It already exists for 1on1's own problems and goes live when Judge0 runs.

## Non-goals and anti-goals

- **No problem statements copied** from LeetCode or Codeforces. They are copyrighted, and LeetCode's terms forbid
  republishing them. We store only metadata and a link.
- **Nothing scraped from DSABuddy** or any site that blocks automated access. LeetCode's own list endpoint returns 403,
  and we don't work around it.
- **No claim that a company asked a question.** Lists say "community-reported (LeetCode company tags, 2022 snapshot)".
- **No in-browser judging of external questions:** we have no test cases for them.
- **"Proctored" means recorded signals only,** never camera, screen capture or lockdown.

## Data sources

| Source | Content | Licence or terms | How it's used |
| --- | --- | --- | --- |
| Codeforces API `problemset.problems` | about 10,000 problems: contest id, index, name, rating, tags | official public API | Name, rating mapped to a difficulty, tags, link; credited "Codeforces" |
| `hxu296/leetcode-company-wise-problems-2022`: `data/leetcode_problems.csv` and `data/companies_and_leetcode_problems.csv` | 1,338 LeetCode problems with link and difficulty; company to problem with occurrence count | MIT (© 2022 Huan Xu) | Name, difficulty, link, companies; credited in the app and in `docs/` |

Codeforces ratings map to difficulty as follows: below 1300 is Easy, 1300–1899 is Medium, 1900 and above is Hard, and an
unrated problem has no difficulty.

## Approach (decided)

- **An import script** (`scripts/import_questions.py`) fetches both sources and writes
  `backend/src/main/resources/external-questions.json`, about 2 MB. Records have this shape:
  `{id, source, title, url, difficulty, tags[], rating?, companies: {name: count}}`. The script is rerun by hand to
  refresh; nothing runs at request time. No database table is needed: the data is read-only reference data, like
  `content.json`.
- **Topic filter:** it uses Codeforces tags and 1on1's own topics. The 2022 LeetCode data carries no tags, so LeetCode
  rows are filterable only by difficulty and company.
- **A Java service** loads the file once and serves `GET /api/v1/bank`, with filters `q`, `source`, `difficulty`,
  `topic`, `company` and paging. 1on1's own problems come first, as source "1on1", with an in-app link. It also serves
  `GET /api/v1/bank/companies`, listing each company and its question count.
- **Mock OA** (`MockService`, stored as per-learner `mock` documents in the existing `Store`, the way coach sessions are, so no migration is needed):
  - Start: choose a size (2 or 3 problems) and a style. "Mixed" draws Easy, Medium and Hard. A company style picks 1on1
    problems in the same proportion of difficulties as that company's list. Duration is 60 or 90 minutes.
  - The server stores the problem ids, the start time and a deadline that it enforces.
  - The score counts each chosen problem with an official ACCEPTED submission created inside the window. It's computed
    from existing submissions; the mock never writes credit itself.
  - The client reports tab switches and fullscreen exits, which the server stores as counts.
  - Finishing early or reaching the deadline locks the attempt. A report shows the score, time used, each problem's
    result and the integrity signals.
- **Frontend:**
  - Practice becomes a hub with tabs: "Our problems" (existing), "Question bank", "Companies" and "Mock OA".
  - The bank is a filterable, paged table whose external rows open in a new tab.
  - The mock page shows a countdown, links to each problem's existing editor (carrying the mock id), and a report.

## Constraints

- No schema change; never reset a learner's database.
- The existing textbook UI, tokens and family marks apply to the new pages.
- Credit both sources visibly on the bank and companies pages.

## Left to the builder

Page size; exact column layout; whether the company page reuses the bank table with a company filter (preferred).
