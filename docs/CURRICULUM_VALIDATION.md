# Curriculum revision — validation and handover

16 November 2026. This checkpoint implements the approved curriculum-first revision. The skill-tree interface remains a decision after review; practice implementation and UI/UX refinement remain Phase 2. No public deployment or push is included.

## Delivered

- 24 core concepts with explicit, acyclic recommended prerequisites, objectives, mental models, worked examples, invariants, common mistakes and complexity assumptions.
- Complete minimal Java teaching sources, line/state annotations and 88 documented normal/boundary/error cases.
- 48 ordered concept-to-question applications resolving to 47 canonical references: 42 external LeetCode references and five original/local references. Reversal is deliberately revisited recursively.
- A version 1 machine-readable manifest and a complete readable curriculum. Each application explains the transfer and any extra prerequisite.
- All 24 old lesson IDs retained, with nine new foundational notebooks: 33 notebooks total, including 26 core/child notebooks and seven advanced notebooks. All 60 original executable problems and 442 fixtures remain.
- Exact topic names, explicit path membership and additive lesson metadata. Existing sorting and memoization/tabulation lessons remain child lessons within their broader concepts.
- An existing-notebook presentation of objectives, recommended prerequisites, Java code and selected external references. No skill-tree surface or new question execution integration was built.
- Nine new concepts have honest worked-state specifications and no unrelated fallback experiment. Interactive readiness is separate from authored content readiness; remaining renderer gaps are recorded per concept.
- DFS corrected to enter and finish one branch before exploring the next sibling. Its regression test checks both entry and reverse return order. Other incomplete visualizations remain explicitly documented.

## Evidence

| Check | Observed result |
| --- | --- |
| Java regression | 56 test methods pass, zero failures/errors. |
| Teaching examples | All 24 complete Java sources compile for release 21; all 88 documented cases pass, including five rejected invalid-bound/shape cases. |
| Existing original references | All 60 Java references pass their existing 442 fixtures. |
| Curriculum integrity | 24 concepts, 47 unique references, 48 associations, valid additional prerequisites and topological order; original IDs and advanced lessons retained. |
| Privacy | Public curriculum and embedded lesson teaching omit checkpoint gold and verification cases; Java remains the grading authority. |
| Data preservation | Actual content seeding preserves an edited lesson, private note, draft, explored state, accepted credit and saved experiment record. Reading-only contexts are owned and do not create activity. |
| Frontend | Nine transport/playback tests pass. Vitest now explicitly scopes to src, avoiding duplicate discovery in ignored rehearsal clones. TypeScript/Vite production build passes; the existing lazy Monaco size warning remains. |
| HTTP integration | Real sessions/CSRF, published content and curriculum, notes/progress, plans, role checks, algorithm evidence methods and logout pass. |
| Determinism | Re-running the authoring generator leaves content.json, curriculum.json and CURRICULUM.md byte-identical. |
| Browser | The complete collection has 15 scenarios. Thirteen passed in the full run; targeted confirmation of the corrected duplicate-link selector and slow practice-screen readiness is recorded below. |

Browser confirmation: both focused checks passed (10.3 seconds). All 15 scenarios have now been observed passing across the full collection and focused follow-up. The last follow-up also verifies that a new learner starts at Time and Space Complexity. The production build passed. The full-run log retains its earlier failures rather than rewriting that history.

The first batched visual review inspected desktop/mobile worked matrices and mobile DFS. Confirmation checked the mobile home and worked model after the copy/readiness changes. No redesign or open-ended polish pass was performed.

Actual provider generation and sandbox grading were not re-run for this content-only revision. The earlier live Gemini result remains historical; Docker/Judge0 execution remains an open gate. No new claim of real acceptance or final assessment readiness is made.

## Source provenance

All 42 selected external canonical URLs were matched in both inspected Amazon CSV snapshots. The checked-in provenance records pin liquidslr revision `2b71796266751b4736a7ef180efb6847879166ee` and snehasishroy revision `e095c259cfd036e3ddb6886e84d7075c2faac477`, with company, file, retrieval date and source snapshot notes. The former has conflicting README/About dates; the latter identifies a 12 July 2026 snapshot.

These observations establish membership in those files, not employer confirmation, statistical independence, current frequency or interview probability. No frequency/acceptance fields, third-party statements, solutions or hidden tests were copied. All teaching prose, hints and Java examples are original. External links can require an account or change availability.

## Reproduce and extend

Run `python scripts/generate_content.py`, `npm run verify`, and, with the app running, `python scripts/verify_api.py` and `npm run test:e2e`. The existing Python/C++ original reference sources were retained; they were not changed or newly certified by this curriculum pass.

Author curriculum content in `scripts/curriculum_content.py`; provenance is checked in beside it. The generator writes both the public content seed and curriculum resource plus the readable curriculum. Do not hand-edit generated artifacts. The API documentation and TypeScript types describe the additive manifest and optional scene behavior. No database migration/reset is required. Administrator-edited notebooks remain preserved and can differ from the canonical curriculum overview.

Local logs are in ignored `.cache/curriculum-verify.log`, `curriculum-http.log`, `curriculum-browser.log` and `curriculum-browser-followup.log`. Browser captures are in ignored `.impeccable/review`. Personal records and credentials are excluded from source transfer.

## Phase 2 backlog

1. Review the authored curriculum with the owner, then decide whether the skill-tree UI is built now or by Phase 2. Use explicit concept dependencies and keep exploration unrestricted.
2. Implement the selected original/integrated practice assignments and external-question presentation; retain shared question identity and each concept's different perspective. Never award solved credit for following an external link.
3. Complete the nine missing matching canvases and the recorded gaps in current renderers. Priorities include variable windows, prefix boundaries, matrices, exact hashing models, arbitrary trees/graphs, full heap operations, backtracking undo and DP state families.
4. Refine the existing interface, motion, mobile code reading and notebook hierarchy. The current revision deliberately uses the existing notebook presentation.
5. Expand instructor forms/publication validation for curriculum content, then finish the previously planned review, dated planning, Blob and document-notebook features.
6. Preserve all old IDs, notes, drafts, attempts and accepted credit through additive changes. The earlier Phase 1 bundle is historical; use the later curriculum checkpoint when transferring this work.
