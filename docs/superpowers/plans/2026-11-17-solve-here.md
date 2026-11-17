# Solve Here Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open any external bank question in 1on1's editor and run it on the learner's own input.

**Architecture:** `BankService` looks up one external record by id. `ExecutionService.submit` accepts a bank id for
unofficial runs only. A new React page reuses `CodeEditor` and polls `/submissions/{id}`, as `ProblemPage` does.

**Tech Stack:** Spring Boot / Java 21, React, react-query, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-17-solve-here-design.md`

## Global Constraints

- Never store or render an external statement. Link to it with `target="_blank" rel="noopener noreferrer"`.
- External ids are accepted only with `official: false`. Otherwise respond 400 with: "External questions run on your
  own input; they are judged on their own site."
- No credit, mastery or mock score from these runs. `ProgressService.accepted` is only reached for official runs.
- Drafts live in `localStorage` under key `1on1-external-draft:<id>:<language>`, read and written inside try/catch.

## Review Focus

1. **An official run sent for an external id** (crafted request): rejected with 400, nothing stored. Pinned in Task 1.
2. **An unknown id** (`cf-nope`): 400, never a 500. Pinned in Task 1.
3. **Judge0 unavailable:** the page shows the server's message and keeps the draft. Pinned in Task 2.
4. **An external id in the coach or mock endpoints:** unaffected, because they read published `problem` documents
   only. Covered by existing tests.
5. **Blocked localStorage** (private window): the editor still works without saving. Covered by the try/catch rule.

---

### Task 1: Backend accepts unofficial runs of bank questions

**Files:**
- Modify: `BankService` (add `Optional<Map<String,Object>> external(String id)`, using a lazily built id-to-record map)
- Modify: `BankController` (add `GET /api/v1/bank/item/{id}`, public, returning the record or 404)
- Modify: `SecurityConfig` (permit `/api/v1/bank/item/*`)
- Modify: `ExecutionService` (field-inject `BankService` with `@Autowired(required = false)`)
- Test: `ExecutionAdapterTest` or a new `ExternalRunTest`

**Behaviour of `submit` when `problem` has an external record:**
- Skip the published-problem lookup.
- Require `official == false`.
- Use the input as the single fixture.
- Unknown `cf-`/`lc-` ids fall through to the existing published-problem check, which returns 400 or 404 as today.

- [ ] **Step 1: Write the failing tests.** Use a `BankService` over a store with no problems and an
  `ExecutionService` with the bank set and a configured runner, as `ExecutionAdapterTest` does. Assert:
  - An official run of `cf-1000A` throws `IllegalArgumentException` with the message above.
  - An unofficial run of `cf-1000A` is stored as a submission with `official` false and one fixture (the input).
  - `bank.external("cf-1000A")` is present, and `bank.external("cf-nope")` is empty.

- [ ] **Step 2: Run** `mvn -q test -Dtest=ExternalRunTest`. Expected: FAIL.
- [ ] **Step 3: Implement the changes above.**
- [ ] **Step 4: Run the test again.** Expected: PASS. Then run the full backend suite.
- [ ] **Step 5: Commit** with the message "Run external bank questions on the learner's own input".

### Task 2: Solve-here page

**Files:**
- Create: `src/pages/practice/SolveExternal.tsx`
- Modify: `src/App.tsx` (add the route `/practice/q/:id`)
- Modify: `src/pages/practice/QuestionBank.tsx` (external rows get a "Solve here" link to `/practice/q/<id>`)
- Modify: `src/styles.css`
- Test: `tests/practice-hub.spec.ts`

**Interfaces:**
- Consumes `GET /bank/item/{id}`, `POST /submissions` with `{problem:id, official:false, language, code, input,
  requestId}`, and `GET /submissions/{id}`.
- The page shows:
  - the title in `.display`, the source, the difficulty and a `FamilyMark`;
  - a statement link labelled "Read the full statement on <source>", followed by the note: "1on1 doesn't copy
    statements. Write your solution here and run it on your own input.";
  - a language select, `CodeEditor`, an input textarea and a Run button;
  - the output (status, stdout and message);
  - any server error from the run, shown verbatim (for example the Judge0 "Configure…" message).

- [ ] **Step 1: Write the failing spec.**
  - From `/practice?tab=bank`, filter by source Codeforces, then click the first "Solve here".
  - The URL matches `/practice/q/cf-`.
  - The statement link has `target=_blank` and points to codeforces.com.
  - Type in the input box and press Run: either output appears, or the message containing "Judge0" appears.
  - Reload: the draft code persists.
- [ ] **Step 2: Run** the spec. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the spec, `npm test` and `tsc`. Expected: PASS.
- [ ] **Step 5: Commit** with the message "Add a solve-here page for external questions".
