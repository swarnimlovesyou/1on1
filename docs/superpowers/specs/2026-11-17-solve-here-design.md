# Solve external questions here — short design (approved)

**Intent:** the owner wants bank questions from LeetCode and Codeforces solvable inside 1on1, with our editor and
compiler. Approved on 17 November 2026 ("Yes, then Learn").

**What it is:**
- Each external bank question gets a page, `/practice/q/<id>`, with:
  - its title, source and difficulty, plus a family mark;
  - a "Read the full statement on <source>" link that opens in a new tab;
  - our code editor (Java, Python, C++);
  - a custom-input box, a Run button and the output.
- The draft is kept per question and language in the browser.
- Bank rows get a "Solve here" link beside the external link.

**What it isn't (constraints):**
- We never store or show the statement. It's copyrighted, and LeetCode's terms forbid republishing it.
- There's no pass/fail verdict: we have no tests for external questions. Runs are always custom runs (`official:
  false`), so they never create credit, mastery or mock scores.
- It needs the Judge0 runner like every run. Without it, the page says so, and the draft is still saved.

**Approaches:**
- **Chosen:** reuse `/submissions` for custom runs. `ExecutionService` accepts a bank id only when `official` is false.
  The existing unofficial-run path stores the input as the single fixture and returns `FINISHED` with stdout.
- **Rejected:** embedding the original site in an iframe. LeetCode and Codeforces block framing, and it would still
  not use our compiler.
- **Rejected:** copying statements and examples into the app. That's copyright and terms violations.
