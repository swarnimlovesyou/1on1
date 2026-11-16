# 1on1 — three-phase implementation and handover plan

Approved delivery plan. Phase 1 belongs to the current owner with Codex; Phases 2 and 3 belong to the two incoming teammates, working sequentially. There are no assumed dates or specialisations. The [feature catalogue](FEATURES.md) defines product scope; [Phase 1 handoff](PHASE1_HANDOFF.md) records implementation status and unresolved gates.

## Curriculum scope amendment — 16 November 2026

The owner moved core curriculum work into the current workstream. The approved 24-concept curriculum is now implemented as content, prerequisite metadata and question assignments; see [CURRICULUM.md](CURRICULUM.md). There are 33 retained/additive notebooks, including child lessons and the advanced branch. Phase 2 retains practice implementation, UI/UX refinement, renderer expansion and review/notebook work. The skill-tree UI is a separate decision after curriculum review. The earlier phase descriptions below remain the baseline, subject to this amendment.

## Delivery approach

Build a working foundation first, then expand the learning experience, then add advanced tools. Each phase includes a refinement pass. Owners may improve layouts, diagrams, animations, explanations and the Blob without replacing dependable contracts or agreed features. Optional enhancements follow the required exit gate; larger ideas go into the backlog.

| Phase | Owner | Finished outcome |
| --- | --- | --- |
| 1. Working foundation | Current owner with Codex | Reliable setup, stable interfaces, real execution and four complete reference journeys. |
| 2. Complete learning platform | Teammate 1 | Full catalogue, learning interactions, planning/review and document notebook. |
| 3. Advanced tools and integrations | Teammate 2 | Own-code tracing, profiling, MCP/skills and a verified final demonstration. |

Keep visual teaching, accessible controls, free exploration, truthful progress and authoritative Java execution throughout. Academic requirements are fulfilled through useful product features rather than becoming the main interface.

## Phase 1 — working foundation and reference experience

**Objective:** hand over a useful, runnable application with proven technical foundations.

### Setup and execution

- Primary development setup: native React/Vite and Java, persistent H2, Docker Desktop for Judge0 and local email testing. Preserve PostgreSQL compatibility without requiring it every day.
- Cross-platform commands: `setup`, `doctor`, `dev`, `stop`, `verify`, `backup`. Preserve existing configuration/data, detect prerequisite/version failures, and never change global Java or PATH settings.
- Prove Judge0 under Docker Desktop first. Add self-hosted authentication, installed-language discovery, resource limits and actual Java/Python/C++ execution.
- Persist jobs and execution tokens, recover known jobs after restart, distinguish compilation errors, wrong answers, timeouts, interruptions and outages. Award accepted credit once.
- Verify Gemini using locally configured credentials. Track actual readiness separately from configuration presence.

If Judge0 fails under the approved Docker Desktop constraint, continue independent work and record the exact blocker. Do not mark grading complete or silently substitute a VM or hosted judge.

### Shared foundations

- Keep one Java application with focused trace, challenge/attempt, progress, execution and tutoring services.
- Typed contracts for lesson blocks, challenges, attempts, saved context and versioned traces.
- Stable entity IDs, semantic operations, independent snapshots and synchronized pseudocode. Preserve identity through duplicate values, pointer changes and structural mutations.
- Grade challenges on Java; initial public responses must omit answer keys.
- Derive achievements/activity from validated events. Autosaves and resume writes never inflate progress.
- Additive migrations preserve accounts, notes, drafts, edited content and progress.

### Four reference journeys

Finish **sliding window, BST, BFS and tabulation**, each with two linked problems:

- Interactive mental model, minimal code, meaningful operation animation and explanation.
- Prediction/manipulation checkpoints, pattern drill and dry run.
- Contextual Gemini help, notes, restored experiment state and real coding practice.
- Keyboard controls, reduced motion, responsive layouts and understandable recovery.

Reusable playback and renderer modules must allow animation refinements without rewriting Java algorithms.

### Exit gate and handover

A fresh checkout demonstrates sign in → lesson → challenge → edited experiment → coding → real acceptance → reload/resume. Verify correct/failing executions in all three languages; accurate saved state and server grading; accepted-only credit; restart recovery and outages; existing algorithms and new contract tests.

Deliver checkpointed source, setup instructions, contract examples, clean sample data, observed verification and a specific Phase 2 backlog. A documented runner blocker leaves the execution gate open even when the remaining foundation is delivered.

## Phase 2 — complete learning experience and notebook

**Objective:** turn the reference experience into the complete everyday product.

### Catalogue and interactions

- Bring all **24 lessons, 60 problems and three paths** to reference quality.
- At least two substantive checkpoints and one pattern drill per lesson; a dry run per visualization family.
- Worked examples, useful prerequisites, invariants, mistakes and complexity explanations replace repetitive prose.
- Complete meaningful animations for arrays/pointers, linear structures, recursion, trees, graphs, DP and advanced structures.
- Every problem gets specific progressive hints, a full editorial, verified Java/Python/C++ references and boundary/adversarial fixtures.
- Administrator forms support preview, validation and publication checks for these contracts.

### Guided transition from concepts to coding

**Phase 2 required scope:** connect the concept lesson to a guided coding workspace. This is planned work, not a claim that the current simulator teaches the complete lesson. Phase 3 enriches it with actual own-code tracing and profiling; those tools are not prerequisites for Phase 2 coaching.

- Teach in context: explain a small visual example, ask for a prediction, connect its state changes to minimal Java code, then offer a related application. Keep free exploration available.
- Start an application with a learner-written approach, invariant and tiny manual example. Offer starter signatures or small implementation milestones appropriate to the learner; avoid revealing the full solution by default.
- Carry the selected concept, problem, language, current draft revision, learner explanation, hint history and actual run results into the Blob's coding conversation. Save milestones and drafts so a learner can resume.
- Use a Socratic coaching ladder: ask one focused question about the learner's reasoning → identify the relevant concept or failing example → offer a targeted hint → explain a small code fragment when needed. A fuller worked solution is available on deliberate request, followed by a transfer task. Do not trap a stuck learner in repeated questions.
- Ground feedback in actual compiler errors, test output and learner-supplied traces. Clearly label suspected mistakes as hypotheses until verified. AI feedback never awards accepted credit; Java grading and isolated execution remain authoritative.
- Point to the relevant code location and ask the learner to predict or make the correction. Suggest edits for review rather than silently replacing their draft. If execution is unavailable, explain the limitation and continue with explicitly labelled reasoning/manual checks.
- Use Socratic prompts throughout: concept prediction ("What must stay true?"), code planning ("What state do you need?"), debugging ("Which smallest input breaks this assumption?"), complexity reflection ("How many times can this pointer move?"), and post-solution transfer ("What changes if negative values are allowed?"). Teach unfamiliar material directly before questioning it.
- Keep hint use separate from correctness and mastery evidence. No accepted credit or mastery upgrade from chat agreement, autosaves or AI opinion.

**Phase 2 acceptance:** demonstrate concept → explained approach → partial code → actual failing run → guided learner correction → actual passing submission → reflection, with reload/resume. Check that an intentionally wrong AI suggestion cannot create credit, full answers are not revealed by default, guidance remains useful after repeated difficulty, and stale code revisions are not presented as current evidence. Verify mobile/keyboard access and honest runner/provider outage recovery.

### Dashboard, planning and review

- Freely explorable concept map, prerequisite links, accessible list and personalised next action.
- Distinguish exploration, passed challenges and accepted problems; explain the evidence behind each state.
- Spaced review uses correctness, hint use and recency: successful reviews after 1, 3 and 7 days; missed reviews return the next day.
- Dated plan tasks support completion, rescheduling and regeneration that preserves completed work.
- Link notes, missed concepts, cards, tasks and review items to their original learning context.

### Blob and document notebook

- Refine the Blob, subtle reactions, contextual actions, persistent conversations and graduated tutoring.
- PDF upload, page-preserving extraction, local retrieval, cited answers and editable revision cards.
- Use [PDFBox](https://pdfbox.apache.org/3.0/getting-started.html) for extraction and [Lucene BM25](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html) for retrieval. Gemini receives selected passages, not the whole library.
- Initially support text PDFs up to 10 MB/100 pages. Slides may be exported to PDF. Explain unsupported scans/password-protected documents.
- Retrieval is restricted to the learner's selected materials and ownership. Preserve file/page citations, and say when sources do not answer a question.
- Generated cards remain editable; self-reported recall is distinct from graded results.

### Exit gate and handover

Verify the entire catalogue, rapid stepping/seeking, meaningful drill feedback, valid alternative dry runs and review scheduling. Check plan regeneration without lost completion, notes/experiments after reload, PDF ingestion/citations/deletion/cross-user isolation, and complete mobile/keyboard/theme/reduced-motion journeys.

Deliver a complete core product, content-authoring guide, stable learning/notebook interfaces, migration evidence and a precise advanced-tools backlog.

## Phase 3 — tracing, profiling, MCP and final integration

**Objective:** add advanced capabilities while preserving the completed learning platform.

### Own-code tracing

- Actual bounded CPython runtime events for primitives, lists, tuples, dictionaries, sets, functions, recursion and references between supported objects.
- Run the tracing harness inside the isolated runner. Python's [tracing API](https://docs.python.org/3/library/sys.html#sys.settrace) observes execution; it does not isolate code.
- Start at 200 source lines, 1,000 captured steps and bounded serialized output. Explicitly report unsupported features/truncation.
- Show source lines, variables, frames, references, mutations, stdout and exceptions.
- Reuse playback controls but keep runtime traces distinct from authored traces. Never fill missing runtime data with AI guesses.
- Enrich Phase 2's guided workspace with these actual runtime events. The coach may discuss a captured frame or mutation, clearly distinguishing observed execution from its interpretation; retain the earlier coaching flow for unsupported languages/features.

### Performance laboratory

- Compare defined operation counts for supported Java algorithms.
- Student-code experiments initially cover sorted searching, sorting, and window/range aggregation.
- Repeatable increasing inputs; record runtime outcomes/timeouts separately from compilation.
- Clearly distinguish theoretical curves, operation counts and measured runtime. Do not claim automatic proof of arbitrary-code complexity.

### MCP and skills

- One thin MCP adapter over existing Java services; no duplicated ownership/grading logic.
- Explicit study-session pairing and browser updates allow assistants to read selected context and open validated experiments.
- Focused tools: context, experiments, dry-run checks, cited notebook search, notes and review cards.
- Package shared teaching guidance as **Concept Coach**, **Exam Practice** and **Debugging Guide**, with client-specific metadata.
- Prove Claude Desktop first, then Codex and ChatGPT using actual tool workflows. Document account/transport restrictions and unverified clients.
- The embedded Gemini Blob remains usable independently of external assistants.

### Final integration and exit gate

Finish cohort, LeetCode, account recovery, admin and usage/error workflows. Run full regression, a fresh-machine rehearsal, PostgreSQL compatibility and preservation of existing data. Refresh benchmarks, baseline comparisons, report, demo, contribution records and limitations.

Every advertised feature needs reproducible evidence. Demonstrate both core learning and advanced tools with actual execution and provider responses. Known limitations remain explicit.

## Shared contracts and transition procedure

Keep API docs, Java DTOs, TypeScript types and fixtures aligned for:

- Versioned traces, stable identity and authoritative Java state.
- Shared challenge attempt grading for predictions, patterns, manipulation and dry runs.
- Saved lesson location, full input/seed, step and relevant code revision.
- Durable jobs, review items, dated plan tasks and notebook citations.
- Additive migrations and explicit compatibility changes; redesigns never reset data.

After each phase:

1. Outgoing owner updates handoff, API examples, setup, feature status, verification, known issues and next backlog.
2. Create a local Git checkpoint and transferable bundle containing history. Exclude keys, personal DBs, uploaded documents, dependencies and caches.
3. Incoming owner restores to a fresh directory, configures their credentials, runs setup/doctor and the prior smoke journey with separate data.
4. Reproduce the demo, inspect migrations and resolve undocumented setup failures before expanding scope.
5. Each teammate records and understands their own contribution and the assessed Java algorithms.

Local checks govern handover; remote CI is separate until the existing GitHub account restriction is resolved. Preserve pre-existing documentation changes. **No push or public deployment is authorised by this plan.**
