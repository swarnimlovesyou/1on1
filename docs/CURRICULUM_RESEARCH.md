# Curriculum research and revision brief

Research date: 16 November 2026. This is a source audit and proposed curriculum, not a claim that new lessons or dataset imports have shipped. Owner scope change: curriculum/content work moves into the current workstream; Phase 2 owns UI/UX refinement and its remaining review/notebook features. The earlier Phase 1 foundation bundle remains a historical checkpoint.

## Sources inspected

| Source | Useful material | Intended use / limits |
| --- | --- | --- |
| [Company questions — snehasishroy](https://github.com/snehasishroy/leetcode-companywise-interview-questions) | CSVs by company and recency, difficulty, acceptance and frequency fields. README identifies a 12 July 2026 snapshot. | Candidate external references and company signals. Community snapshot, not employer-verified evidence or a current interview probability. Repository describes Premium-based collection; redistribution permission not established. |
| [Company questions — liquidslr](https://github.com/liquidslr/leetcode-company-wise-problems) | Company folders with time-window CSVs. | Cross-check signals only. About says 20 October 2025 while README says 1 June 2025; record dates per source rather than invent freshness. Redistribution permission not established. |
| [Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/study-cheatsheet/) | Topic guides, complexity, corner cases and recommended practice. | Coverage audit: arrays, strings, hash tables, matrix, linked lists, stack/queue, intervals, trees, graphs, heaps, tries, DP and binary techniques. Author original teaching content. |
| [Grind 75 methodology](https://www.techinterviewhandbook.org/grind75/faq) | Curated practice progression based on patterns, difficulty and other relevance signals. | Build easy introductions followed by transfer/mixed practice; do not replace concept coverage with company frequency. It explicitly favours learning patterns over predicting company questions. |
| [CSES Problem Set](https://cses.fi/problemset/) | Sorting/searching, DP, graph, range/tree and other algorithm problem categories. | Advanced coverage and external practice links; not a company-labelled dataset. Do not copy statements/test data without permission. |
| [MIT 6.006](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/) | Academic course, lectures, assignments and analysis. | Check conceptual accuracy/prerequisites and complexity reasoning. Reuse requires following the actual material's licence/attribution conditions. |
| [NeetCode roadmap](https://neetcode.io/roadmap) | Candidate interview roadmap. | Page is client-rendered and did not expose its topic graph to the research reader. Do not claim a full audit or dataset extraction. |

These sources serve different purposes. Company CSVs provide question metadata; curated lists provide practice selection; academic sources support understanding. Public GitHub visibility alone does not establish a licence to redistribute third-party material. Keep original local problems; link externally for referenced interview questions. No paid access was bypassed or credentials supplied to source scrapers.

## Current application audit

Inspected generated content and authoring script: 24 lessons, 60 original problems, three paths. Only sliding window, BST, BFS and tabulation have the expanded reference treatment.

- Two Pointers is the first lesson; Arrays/Strings, complexity and hash maps/sets have no dedicated foundation lessons.
- Most prerequisites are simply the preceding entry in the generator. That makes unrelated dependencies and is not a pedagogical graph.
- Missing dedicated instruction includes prefix sums, intervals, matrices, monotonic stacks, DSU, topological sort, binary-search boundaries/answer space and common DP families.
- Memoization/tabulation need progression beyond Fibonacci; BFS/DFS need grid and structural applications.
- Generic checkpoint wording and default input shapes are repeated across much of the catalogue.
- The path labelled interview currently concentrates trie, set cover, Quickselect and Bloom filters, rather than broad interview patterns.
- Poetic titles obscure discoverability. Display exact method names; supporting copy may explain the intuition.
- Incomplete renderers must not be mistaken for complete lessons. Track content correctness separately from the Phase 2 visual refinement pass.

## Proposed curriculum structure

This is a recommended expansion, not a silent commitment to a new lesson count. A module may contain multiple short lessons. Keep existing IDs where the concept is unchanged so saved work survives.

| Stage | Modules / concepts | Main dependency |
| --- | --- | --- |
| Foundations | Complexity and constraints; arrays/strings; hash maps/sets; basic sorting; prefix sums | Basic programming |
| Core patterns | Two pointers; fixed/variable sliding windows; binary search and boundaries; intervals; matrices | Arrays, ordering, hashing |
| Linear structures | Linked lists; stacks/queues; fast/slow pointers; monotonic stack | Arrays, references |
| Recursive structures | Recursion/call stack; backtracking; tree DFS/BFS; BST; heaps/priority queues | Stacks, recursion |
| Graphs | Representation; BFS/DFS and grids; topological sort; DSU; Dijkstra | Queues, recursion, heaps |
| Dynamic programming | State/transition/base cases; memoization/tabulation; 1D, grid, knapsack/subset and sequence patterns | Recursion, dependency ordering |
| Interview transfer | Mixed pattern identification; constraints-to-complexity; counterexamples; company-filtered external practice | Relevant concepts, no hard locks |
| Advanced algorithms / course | Tries/text search; balanced trees/range queries; max flow/matching; set-cover approximation; randomized selection; Bloom filters | Appropriate trees/graphs/hashing foundations |

Retain three navigable paths: DSA Foundations, Interview Patterns, Advanced Algorithms. Paths can overlap; advanced academic material remains useful and does not displace beginner foundations. Keep free exploration and show recommended prerequisites.

## Learning standard per concept

1. Exact topic title and observable learning objectives.
2. Prerequisites and a concrete problem the method addresses.
3. Manipulable visual model with authoritative states; state the visualization's supported input limits.
4. Worked example, invariant, minimal code and synchronized explanation.
5. Counterexample, common mistake and complexity assumptions.
6. Prediction/manipulation checkpoint, pattern recognition and dry run.
7. Easy canonical practice, a meaningful variation, then mixed transfer practice.
8. Reflection/review linked to the concept and evidence of attempted work.

A visualization audit must check the actual operation sequence and final state, duplicates/empty or invalid inputs, code-line synchronization, backward stepping and seeking. Academic correctness repairs belong with curriculum work now; visual styling, layout, animation polish and broader UI/UX belong to Phase 2.

## Dataset design and selection method

Keep external interview references separate from executable original problems. Suggested records:

- Stable platform/problem ID and canonical URL; title, topic/pattern tags and difficulty.
- Source repository/file, pinned revision, retrievedAt and source snapshot date.
- Company, time window, raw frequency value and its source-defined meaning (unknown when undocumented).
- Access restriction, reuse/licence status, concept mapping and duplicate-source lineage.
- Local original problem mapping only where the learning objective genuinely matches. Never imply that a similar original exercise was asked by a company.

Deduplicate by platform ID/URL, not title. Do not add together frequency fields from overlapping snapshots or treat two copied repositories as independent confirmation. Preserve raw scales; no fabricated cross-company likelihood score. Unknown company provenance remains unknown.

Prioritise concept coverage and prerequisites first, then pedagogical quality, difficulty progression and independent curated-list agreement. Use company recency/frequency as a secondary filter. Every included reference needs a curriculum role; importing thousands of links is not a learning experience.

## Implementation sequence

1. Normalise all existing topic titles and replace list-order prerequisites with an explicit graph. Preserve IDs/progress.
2. Produce a machine-readable concept inventory and coverage map for all 60 original problems; distinguish absent, basic, reference-quality and verified lessons.
3. Add missing foundational teaching and repair incorrect/incomplete learning states. Avoid assigning an unrelated visualization to a new topic merely to fill a card.
4. Build a small provenance-aware external question index after file/schema and reuse review; retain links when redistribution rights are uncertain.
5. Re-author lessons/problems in dependency order and validate code, fixtures and drill feedback.
6. Give Phase 2 a concrete UI/UX backlog built on the corrected curriculum and stable contracts.

No UI changes, live content imports or repository push were performed in this research pass. Curriculum scope expansion and the new source evidence must be carried into the next implementation checkpoint; the previous bundle will not contain this research until repackaged.
