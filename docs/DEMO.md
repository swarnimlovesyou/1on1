# Demonstration and assessment evidence

> Phase 1 update (16 November 2026): see [current handoff](PHASE1_HANDOFF.md) and [validation](VALIDATION.md). This earlier academic baseline/demo outline must be refreshed in Phase 3; it is not evidence that later planned features or live grading are complete.

## Approximately eight-minute flow

1. **0:00–1:00 — Real problem and user.** Explain fragmented DSA study. Open the learning space and an interactive notebook.
2. **1:00–2:20 — Authentic algorithm execution.** Run sliding window on a changed input, step through state/pseudocode, explain the running-sum invariant. Enter an invalid window size and show the recovery message.
3. **2:20–3:20 — Learn to practise.** Answer a checkpoint, save a private explanation, open the linked problem. Show draft recovery. If configured, run Java/Python/C++ in the hosted sandbox and explain official versus custom runs. Otherwise explicitly demonstrate the missing-service state; do not pretend it is a live grading result.
4. **3:20–4:40 — Advanced algorithm workflow.** Select topics/difficulty and generate a plan. Explain the set-cover model, the gain of each selected problem, uncovered topics and why the answer is approximate.
5. **4:40–5:30 — Search and CO5.** Search a concept prefix and show the Java trie. Open cohort summaries and explain randomized selection, duplicate scores and nearest-rank quartiles. A small cohort legitimately has no quartile summary yet; use the evidence dataset to show scale.
6. **5:30–6:20 — Helpful AI.** If configured, ask why a selected step happened or request a supported visual example. Explain that Java computes states and the model supplies guidance/parameters. Demonstrate error handling if the free tier is exhausted.
7. **6:20–7:30 — Evidence.** Run one benchmark, compare against the baseline, show test results and raw JSON. Identify a case where the optimized technique may not help.
8. **7:30–8:00 — Reproducibility.** Show setup steps, persistent data, test commands, actual contributions and known service limitations.

## Requirement mapping

| Requirement | Evidence |
| --- | --- |
| Genuine application workflow | Notebook → experiment → checkpoint → notes → judged practice → plan/progress. |
| Java backend and own business logic | Spring controllers/services, custom algorithm classes, deterministic Java traces and output comparison. |
| Working frontend integration | Same-origin API client with sessions/CSRF; browser journeys and production build. |
| Two or more distinct techniques, Units 4–6 | Trie, greedy set cover and randomized Quickselect. |
| Meaningful CO5 | Independent cohort-summary selection and scaled Quickselect comparison. |
| Inputs/outputs/assumptions/failures | API contracts, explicit trace limits, impossible plan coverage, provider errors and technical report. |
| At least five tests per core method | `AlgorithmsTest`; exact small-instance and sorted-reference oracles. |
| At least three benchmark sizes | Evidence endpoint and reproducible JSON exports. |
| Baseline comparison | Trie versus scan, Quickselect versus sort, set cover versus first-useful selection. |
| Realistic data | Original content, real native user actions, external profiles and labelled synthetic benchmark generators. |
| Runnable source and documentation | Maven/npm, SQL migration, compose, README, API docs and CI. |
| Individual contribution/viva | Team must record actual names/IDs/contributions; review commit history and explain critical Java methods. |

## Viva preparation

Explain why an algorithm belongs in the product, not only its pseudocode. Be ready to change a test input and reason about the result. For Quickselect, distinguish expected and worst-case time; for set cover, distinguish correctness of coverage from exact minimum size; for trie, separate index construction from bounded query/output work. Explain where the frontend renders state and where Java computes it. Know how a hidden judge case is protected and why a Bloom-filter lesson describes positives as uncertain.
