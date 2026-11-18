# Revamp phase B: Home dashboard and "I was asked this" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Home tells a learner what to do next, how active they are, what is happening (contests) and what has been
asked recently, from learners' own reports; the old Home's layout gap goes with it.

**Architecture:** A `ReportController` stores learners' "I was asked this" reports as documents (one per learner,
question and company) and serves recent ones aggregated. Home is rebuilt from data the app already has (learning map's
next action and due reviews, progress activity, contests) plus the reports.

**Spec:** `docs/superpowers/specs/2026-11-18-revamp-design.md` phase B.

## Global Constraints
- Reports are labelled as learner-reported, with month and count; never mixed into the 2022 dataset's numbers.
- A report needs a signed-in learner, a real bank question and a plausible company name; one per learner, question and
  company.
- Home renders for guests (no activity) and when any one source fails.

## Review Focus
1. **Duplicate or junk reports** (same learner again, unknown question, "<script>" company): rejected. Task 1.
2. **Guest on Home:** sees next step, contests and recent reports; no broken activity. Task 3.
3. **Streak across days with no activity / time zones:** streak counts consecutive days up to today or yesterday. Task 3.
4. **Recently asked with no reports yet:** says so and points to the company lists. Task 3.
5. **Phone width:** no sideways scroll. Task 3.

### Task 1: Reports API
- `POST /api/v1/reports {questionId, company, stage}` (signed in; stage `OA` | `Interview`), `GET /api/v1/reports/recent`
  (public): `[{questionId, title, url, source, company, stage, month, reports}]`, newest first, max 8.
- `ReportTest`: stores and aggregates; duplicate is idempotent; unknown question 404; bad company 400; guest 401.

### Task 2: "I was asked this" on the solve page
- A small form (company, stage) on `/practice/q/:id`; signed-out learners see a sign-in link. Spec in `tests/reports.spec.ts`.

### Task 3: Home dashboard
- Greeting; next step (learning map) with up to two more actions (due review, plan task); activity: streak, this week,
  12-week heatmap, totals; what's happening: next contests; recently asked: learner reports; quick links with keys.
- `src/pages/home/activity.ts` (`streak`, `weekCount`, `weeks`) with Vitest; `tests/home.spec.ts`.
