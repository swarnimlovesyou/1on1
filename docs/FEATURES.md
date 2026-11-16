# 1on1 — consolidated feature catalogue

Last updated: 15 November 2026.

This document captures the product ideas and decisions agreed with the owner. It describes the intended platform, not a claim that these features are complete. Phase 1 now provides four expanded reference journeys and shared foundations; the full catalogue, review/notebook and advanced tools still require the assigned later phases. Actual Gemini passed, while Docker Desktop blocks actual Judge0 verification. See [PHASE1_HANDOFF.md](PHASE1_HANDOFF.md), [the three-phase plan](IMPLEMENTATION_PLAN.md) and [VALIDATION.md](VALIDATION.md) for current status.

## Curriculum scope update

The owner moved the core curriculum into current work: 24 concepts, 33 notebooks including retained child/advanced lessons, and 1–2 selected question applications per concept. Practice implementation and UI/UX remain Phase 2. The skill-tree interface will be decided after curriculum review. See [the implemented curriculum](CURRICULUM.md).

## Product direction

**Make it click.** Help learners internalize DSA by manipulating visual models, connecting them to minimal code, recognizing patterns, solving problems, and revisiting mistakes.

The typical journey is:

**Concept map → visual mental model → minimal code → pattern drill → dry run → coding practice → reflection and spaced review.**

This is guidance, not a compulsory sequence. Lessons and experiments stay accessible without passing prerequisite checkpoints. Build a complete, polished platform whose academic requirements are fulfilled through useful features.

## 1. Home dashboard and concept map

- An interactive skill tree showing core concepts, their relationships, and recommended prerequisites: arrays, linked lists, stacks, queues, recursion, trees, heaps, graphs, dynamic programming, and advanced techniques.
- Freely accessible nodes with a simpler list view for small screens and accessibility.
- A personal next action: resume a lesson, retry a weak concept, finish a planned problem, or complete a due review.
- Evidence-based states such as explored, practising, demonstrated, and review due. Show what supports each state rather than inventing precise mastery percentages.
- Review urgency informed by correctness, hint use, previous attempts, and elapsed time. Completed work remains recorded when a review becomes due.
- A dashboard that reflects actual activity and onboarding goals; autosaving or leaving a tab open does not count as studying.

## 2. Interactive concept notebooks

- Begin with a visual mental model that can be manipulated before introducing syntax.
- Short teaching sections covering intuition, a worked example, the invariant, minimal implementation, complexity, and common mistakes.
- Link highlighted code or pseudocode directly to the operation shown in the diagram.
- Prediction checkpoints: ask what changes next, which pointer moves, or why a state is valid.
- Input-manipulation challenges: find an input that exposes a mistake, reaches a target, or demonstrates an edge case.
- Contextual links from a lesson to relevant drills and coding problems.
- Save the current section, input, trace step, and notes so the learner can resume.
- Retain the planned scope of 24 substantial lessons and three learning paths. Replace thin or repetitive content rather than increasing counts as a substitute for quality.

## 3. Animated algorithm laboratory

- Faithful operation animations: moving array elements and pointers, sliding window boundaries, stack/queue insertions, linked-list pointer changes, tree rotations, graph exploration, and DP dependencies.
- Cover the existing algorithm catalogue, including sorting/searching, recursion/backtracking, trees/heaps, graph algorithms, DP, tries, greedy set cover, randomized Quickselect, and Bloom filters.
- Stable identities for elements and nodes, including duplicate values, so animations show what actually moved.
- Play/pause, step forward/back, scrub, replay, speed controls, editable inputs, and boundary-case presets.
- Synchronized explanation, variables, code highlighting, and a readable transcript.
- Java-generated authoritative traces. The frontend renders and animates them; AI may propose validated inputs for supported scenes.
- Keyboard operation, reduced motion, responsive layouts, and interruption-safe playback.

## 4. Pattern-recognition drills

- Short, approximately two-minute “Spot the Pattern” exercises before full coding problems.
- Present a problem prompt and constraints, then ask for a suitable pattern, target complexity, and a short explanation.
- Accept multiple valid approaches where appropriate. Constraints inform the answer but do not uniquely determine it.
- Explain why an approach fits and why plausible alternatives fail.
- Connect missed patterns to the relevant lesson, experiment, and review queue.

## 5. Dry-run and exam-practice mode

- Interactive state tables for manually tracing algorithms: pointer positions, variable values, recursion state, partitions, queues, visited sets, and distance tables.
- Check submitted steps against Java-computed transitions and algorithm rules, accepting alternative valid tie-breaking or traversal choices.
- Identify the first incorrect step and let the learner retry from there.
- Gemini explains the mistake and offers graduated hints; deterministic checks establish correctness.
- Exam-style questions and quizzes grounded in lessons and, when selected, the learner's uploaded materials.
- Preserve attempts and useful explanations for later review.

## 6. Coding practice and real grading

- Retain 60 original problems with useful statements, constraints, samples, and lesson connections.
- Java, Python, and C++ editing, appropriate starter code, and saved drafts per problem/language.
- Custom runs, sample tests, official submissions, readable compiler/runtime errors, and submission history.
- Real isolated execution through a locally integrated Judge0 service, with resource limits and clear unavailable/interrupted states.
- Private hidden tests and accepted-only native solved credit, awarded once per problem.
- Problem-specific progressive hints, editorials, complexity explanations, and verified reference solutions in the supported languages.
- Boundary and adversarial tests that reject plausible incorrect solutions.

## 7. Own-code tracing and visual performance tools

### Trace my code

- Step through the learner's real executed code with source-line highlighting, variables, collections, references, and visible mutations.
- Initial scope: short Python programs, small inputs, supported built-in structures, and a capped execution trace.
- Capture actual execution inside an isolated runtime. Do not substitute an AI-generated account of what the code probably did.
- Report unsupported features and truncated traces explicitly. Normal Java/Python/C++ grading remains a separate capability.
- Treat broader language and structure support as an extension of a verified tracer, not an existing prototype capability.

### Visual Big-O profiler

- Compare brute-force and improved approaches as input size grows.
- Begin with supported algorithm implementations and defined operation counts, such as comparisons, visits, or moves.
- Add measured runtime experiments for student code with consistent inputs and execution limits.
- Distinguish theoretical growth curves, measured operation counts, and measured runtime. A few samples do not prove an arbitrary program's Big-O or an exact future TLE threshold.
- Animate the relationship between additional work and growth so the chart teaches a concrete tradeoff.

## 8. Contextual AI companion — “The Blob”

- A small, clickable companion opening contextual chat beside the learning workspace.
- Quiet idle behavior, subtle reactions, and brief acknowledgements tied to meaningful actions.
- Explain the current algorithm step, invariant, code line, or variable state.
- Give Socratic, graduated hints and let the learner deliberately request a fuller explanation.
- Turn natural-language questions into validated experiments using supported visual scenes.
- Help debug using the learner's code and visible execution results; explain checkpoint and dry-run mistakes.
- Generate editable flashcards, refresher questions, and exam quizzes from validated lessons or cited study materials.
- Save conversations with their lesson/problem context; support cancelling responses and recovering from unavailable service.
- Gemini is the planned in-platform provider. Its internet connection and free-tier limits still apply to a locally running website.

## 9. Personal notebook and document-based exam preparation

- Notes, bookmarks, saved explanations, and experiment snapshots linked to lessons and problems.
- Reopen the associated experiment, input, and step from a note.
- Upload lecture PDFs and slides exported as PDFs initially; retain document and page references during extraction/indexing.
- Search the learner's selected materials and provide grounded answers with file/page citations.
- State when the selected sources do not support an answer.
- Generate review cards and exam questions from selected notes or documents, with learner preview/editing.
- Keep files and indexes local where practical. Confirm model compatibility, quotas, and any service costs before selecting managed retrieval.
- Scope notebook retrieval to the connected learner and selected materials.

## 10. Claude, ChatGPT, and Codex integration through MCP

- One shared MCP adapter over the Java APIs, avoiding duplicated grading or algorithm logic.
- Explicitly connect a study session so the assistant can obtain the selected lesson, experiment state, code context, and relevant learning history.
- Expose focused tools to retrieve context, create/open validated experiments, check dry runs, search cited notes, and save explanations or review items.
- Synchronize requested experiment changes into the website through a defined browser/backend update channel.
- Keep authorization, validation, grading, and achievement updates enforced by Java.
- Share refined teaching guidance across clients, packaged as focused skills such as **Concept Coach**, **Exam Practice**, and **Debugging Guide**, with client-specific metadata and connection setup where needed.
- Prove the first local workflow with Claude Desktop, then package/test ChatGPT and Codex support against their actual connection requirements.
- Claude Desktop supports local MCP extensions. Hosted ChatGPT requires an appropriate reachable connection; Secure MCP Tunnel is a documented option for private/local servers, subject to account/workspace support.
- External-assistant mode runs inside Claude/ChatGPT/Codex. The website's Blob continues to use its own model integration; MCP does not automatically embed a subscription chat session into the website.
- Public marketplace distribution and public website deployment are outside the local milestone.

References: [Claude local MCP](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop), [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## 11. Review, planning, and supporting platform features

- Spaced review covering missed concepts, prediction/drill attempts, saved flashcards, and due refreshers.
- Initial review schedule: successful material returns after 1, 3, and 7 days; a missed review returns the following day. Validate and refine this simple rule using actual learner behavior.
- Practice plans with selected topics, dated tasks, completion, rescheduling, and regeneration that preserves finished work.
- Clear progress summaries distinguishing explored lessons, passed checkpoints, and accepted native problems.
- Account creation, sign-in, onboarding, recovery, preferences, and reliable persistence.
- Optional study cohorts and genuine cohort summaries.
- LeetCode public-profile connection with cached/stale/unavailable states; imported statistics stay distinct from native achievements.
- Administrator content forms, preview, validation, publication controls, import/export, and usage visibility.

## 12. Visual personality and polish

- Preserve the interactive notebook identity, Geist/JetBrains Mono typography, cobalt emphasis, and light/dark/system themes.
- Increase readability, hierarchy, control sizes, and breathing room.
- Add restrained navigation transitions, useful interaction feedback, and brief completion moments.
- Give algorithm operations the strongest motion; keep surrounding motion supportive.
- Challenges and quiet milestones provide engagement. No XP/level economy, compulsory unlocks, constant mascot movement, or excessive effects.
- Provide complete loading, empty, unavailable, error, and recovery states, including accessible mobile behavior.

## Delivery boundaries and definition of completion

- **Local-first; public deployment is not required for this milestone.** Setup must be reproducible and the full learning-to-practice journey demonstrable.
- **Docker Desktop only for the local judge.** No separate Ubuntu VM was approved. Judge compatibility remains to be proven; failure is an explicit blocker for local grading, not permission to claim it works or silently switch hosting.
- **Java remains responsible for core algorithms and business logic.** Preserve the original trie, greedy set cover, randomized Quickselect/CO5 component, correctness tests, baseline comparisons, three-size benchmarks, and assessment documentation.
- **Complete one reference journey, then apply the standard across the catalogue.** Start with sliding window plus a linked problem, including saved context, meaningful interaction, actual AI help, and real grading. This first slice does not reduce the final 24-lesson/60-problem scope.
- **Verify real integrations and real behavior.** Contract tests, catalogue counts, or a visible interface alone do not demonstrate live AI, execution, educational quality, or reliable saved progress.
- **Keep the current handoff edits and subsequent work local and unpushed** until the owner requests publication. Compiling this catalogue does not start feature implementation.
