# 1on1: Interactive DSA Learning and Practice

> Phase 1 update (16 November 2026): see [current handoff](PHASE1_HANDOFF.md) and [validation](VALIDATION.md). This earlier academic baseline/demo outline must be refreshed in Phase 3; it is not evidence that later planned features or live grading are complete.

**Course:** Advanced Algorithm, Semester V, CIA 3, 2026–27.

**Team:** Two or three students. Record official student names/IDs and actual contributions before faculty submission; these personal details have not been supplied.

**Repository:** https://github.com/swarnimlovesyou/1on1

## Problem and target users

Students often move between written explanations, videos, coding sites, and spreadsheets without forming a clear connection between an algorithm's invariant and its execution. A solved counter alone does not explain where understanding is missing. College students need a place to change a small input, observe the real state transitions, express the idea in their own words, and immediately practise it.

1on1 is a visual learning platform organized around interactive study notebooks. It combines authored lessons, deterministic Java traces, checkpoints, an integrated coding workspace, revision notes, purposeful practice plans, progress, study cohorts, and public LeetCode statistics. Gemini supplies contextual explanations and validated experiment parameters. It does not generate authoritative execution states or grade submissions.

## Algorithm-driven features

1. **Trie (Unit 4):** Prefix indexing of lesson titles, concept names, and problem titles. A cached index provides bounded results without rescanning the complete catalog per query. The index is rebuilt when content changes.
2. **Greedy set-cover approximation (Unit 5):** Select questions adding the most uncovered requested topics, subject to difficulty filters and already-solved exclusions. Show each selected question's contribution and any infeasible topic coverage. The application states that the result is approximate.
3. **Randomized Quickselect (Unit 6 / CO5):** Compute activity-score quartile thresholds for a cohort summary without sorting all members. A separate summary API supports progress views that do not need a leaderboard. Three-way partitioning handles duplicates and defensive copies preserve caller data.

All assessed algorithms are custom Java implementations. Spring provides HTTP, security, database access and application infrastructure. Java Collections support storage, not replacements for assessed methods.

## Workflow and scope

A learner opens a concept notebook, changes its input, steps through Java-computed states, predicts the next action, saves a personal explanation, and opens related practice. Java/Python/C++ submissions execute through an isolated hosted judge. Java compares output with public and hidden fixtures and updates native progress after acceptance. The planner uses real catalog topics to create a focused set of questions. Cohorts summarize activity; LeetCode activity remains separately identified.

The release contains 24 lessons, 60 original questions, 420 judge fixtures, three learning paths, twelve reusable visualization families, accounts, persistent state, and an administrator content workflow.

## Data, constraints and feasibility

Original authored lessons/problems and realistic synthetic benchmark datasets are committed with a deterministic generator. Real native progress is generated only by user actions and accepted official submissions. LeetCode uses public profile data and a cached, unofficial connector; availability and historical coverage are explicitly limited.

Interactive traces accept bounded inputs: 1–32 integers, small graph/tree/table scenes, and at most 200 characters of word input. Judge source is capped at 50,000 characters; test count and resource limits are bounded. Hidden data is never returned to the browser or tutor. Invalid input, empty goals, unreachable coverage, duplicate values, unavailable services and permission failures are handled explicitly.

## Measurable success criteria

- A new learner can complete the notebook-to-practice journey and recover saved work after reloading.
- At least five documented tests per assessed algorithm, including boundary cases, pass alongside trace and reference-fixture verification.
- Each assessed algorithm is benchmarked at three increasing sizes with a stated baseline, warm-up, repeated measurements and hardware metadata.
- Search results match the chosen prefix semantics; generated plans cover all feasible requested topics; cohort quartiles agree with sorted reference data.
- Frontend and Java run from written setup steps; the full workflow is demonstrable locally without fabricated AI or grading responses.

## Contributions and demonstration

Allocate primary responsibilities across frontend/notebooks, Java/algorithms/data, and AI/execution/integrations, sharing content review and testing. Record real work through Git commits and an individual contribution table in the final report. Demonstrate a realistic learning session, invalid-input recovery, algorithm-driven planning, and measured evidence within approximately eight minutes. Each student should explain their contribution and a critical Java method during the viva.
