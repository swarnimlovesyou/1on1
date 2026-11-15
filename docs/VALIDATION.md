# Validation record — 16 November 2026

This records the Phase 1 foundation. The earlier 15 November record is retained below as historical evidence; its live-provider gaps and counts are superseded here.

| Check | Observed result |
| --- | --- |
| Java tests | 49 passed, zero errors/failures: Algorithms 16, Content 1, ExecutionAdapter 12, LearningEvidence 10, Trace 10. |
| Java authored references | All 60 pass 442 public/hidden fixtures. |
| Python/C++ authored references | Eight references in each language pass 78 fixture executions per language. These are trusted-source checks, not student sandbox execution. |
| Frontend | Nine unit tests pass; TypeScript/Vite production build passes. Existing lazy Monaco chunk still emits a size warning. |
| Browser | 12 scenarios pass on the actual native app, including four reference journeys, reload state/activity, tutor-history retry/context, keyboard/reduced motion and responsive/dark layouts. |
| HTTP | Real sessions/CSRF, content privacy, accounts, notes/progress/plans, role checks, evidence methods and logout pass. |
| Actual Gemini | Explanation, Java-validated scene and streamed provider tokens pass with locally configured credentials and gemini-3.1-flash-lite. No key was committed or printed. |
| Actual Judge0 | Blocked: local language discovery cannot reach the runner. This is not a pass or accepted submission. |
| Migration/persistence | Existing persistent H2 opens at additive schema V2. Context, drafts, notes and attempts survive reload; autosaves do not create activity. |
| Backup command | Stopped native H2 copied into ignored timestamped backup; the existing database reopened without reset. |
| Visual review | Initial eight reference captures reviewed; one readability/label/code-highlight batch applied. Confirmation reviewed mobile BFS/BST and desktop sliding window; diagram overflow is local. No unbounded cosmetic iteration. |

The full live command records `execution: blocked`, `ai: passed` and exits nonzero. Java execution-contract tests use an isolated local HTTP fixture, including language/authentication selection, uncertain dispatch, saved-receipt recovery, expiry and idempotent acceptance. They do not prove live Judge0 sandbox compatibility.

## Docker and other open gates

Docker Desktop initially answered with engine 27.5.1, Linux x86_64 and cgroup v2. The official Judge0 1.13.1 image pull failed with unexpected EOF; one retry was followed by daemon unresponsiveness. Docker backend logs reported a SCSI device being offlined after error recovery. No data volumes were deleted and no VM/hosted fallback was selected. See [the exact blocker and recovery](PHASE1_HANDOFF.md).

Mailpit delivery, real three-language execution, Docker sandbox/cgroup compatibility and PostgreSQL remain unverified. LeetCode live upstream availability remains separate. GitHub CI has not run because of the earlier account-level restriction; passing local checks do not imply remote CI success. Other operating systems and a genuinely fresh machine still need rehearsal.

## Reproduce

Use `npm run setup`, `npm run doctor`, `npm run verify`, `npm run verify:references`; with the app running use `python scripts/verify_api.py`, `npm run test:e2e` and `npm run verify:live`. Install Playwright Chromium first. The last command requires actual integrations and fails when a required service is blocked. `--ai-only` and `--judge-only` are scoped checks, not a replacement for the complete gate.

Local evidence is retained under ignored `.cache` (final-verify/build/browser/http/live logs, reference-verification.json, live-verification.json) and `.impeccable/review` (screenshots). The bundle excludes these personal/generated files; committed results and public contract fixtures provide the transfer record.

## Clean-source rehearsal

Pending the outgoing local source checkpoint; the result will be recorded here before final handover.

---

# Validation record — 15 November 2026

## Executed checks

| Check | Observed result |
| --- | --- |
| Java compilation / JUnit | 31 test methods, 0 failures/errors across AlgorithmsTest (16), TraceTest (9), ContentTest (1), ExecutionAdapterTest (5). |
| Original problem fixtures | All 60 Java reference solutions compiled and passed all 420 public/hidden fixtures inside ContentTest. |
| Frontend API / streaming | 6 Vitest tests passed: CSRF, service errors, invalid JSON, streamed token assembly, interruption, provider-quota error. |
| Real HTTP integration | Passed published-content counts, hidden-data stripping, CSRF rejection, registration/session, persisted learning/notes, planner coverage, administrator denial, unavailable-runner exclusion, all three benchmark methods and logout. |
| Administrator HTTP workflow | Configured editor login, private fixture access, validated draft save, and draft exclusion from the public catalog passed. |
| Guest browser journey | Passed concept discovery, trace stepping, prediction checkpoint and linked coding workspace. |
| Student browser journey | Passed registration/onboarding, notes surviving reload, practice-plan creation and cohort creation. |
| Saved work browser journey | Passed Java draft autosave/recovery and notebook step recovery after a fresh load. |
| Responsive/light | Home, notebook, practice and login captured at 1440 and 390 pixels; no horizontal page overflow or application errors. |
| Dark/tablet | Notebook verified at 1440, 1024, 768 and 390 pixels; dark screenshots at desktop/mobile widths. |
| Production frontend | TypeScript and Vite production build passed. Editor is lazy-loaded; only Java/Python/C++ language support and Latin font subsets ship. |
| Dependency audit | npm audit reported 0 vulnerabilities after updating the test dependency chain. |
| Impeccable detector | Returned an empty findings array. |
| Fresh visual review | All ten screenshots reviewed. Three material home/mobile issues were corrected in one batch. Reviewer rescored all three as resolved, disposition `ship`; this follow-up scored those fixes, not a new full review. |
| Container configuration | `docker compose --env-file .env.example config --quiet` passed. |

## Observed benchmark data

Environment: Java 25.0.4.1, Windows 11, 32 logical processors. Seed 42, two warm-ups, five measured repetitions. The Java code compiles for release 21. These are local in-process measurements, not production-service latency.

| Technique | Input | Algorithm mean ms | Baseline mean ms | Quality observation |
| --- | ---: | ---: | ---: | --- |
| Quickselect | 1,000 | 0.04374 | 0.08910 | Same order-statistic definition. |
| Quickselect | 10,000 | 0.59806 | 1.87926 | Full sorting is the baseline. |
| Quickselect | 100,000 | 6.21938 | 22.70114 | Expected improvement on this input; no worst-case guarantee. |
| Trie | 1,000 | 0.03204 | 0.13430 | Index construction excluded. |
| Trie | 10,000 | 0.13746 | 1.31244 | Bounded prefix enumeration. |
| Trie | 100,000 | 0.06134 | 14.49820 | Query timing varies with JVM/cache/noise. |
| Set cover | 100 | 2.81792 | 0.07974 | 10 selected versus 15; all topics covered. |
| Set cover | 1,000 | 31.43292 | 0.09592 | 9 selected versus 15; all topics covered. |
| Set cover | 10,000 | 294.26538 | 0.09720 | 8 selected versus 15; all topics covered. |

Raw records: [Quickselect](benchmarks/quickselect.json), [trie](benchmarks/trie.json), [set cover](benchmarks/set-cover.json). Greedy set cover trades additional computation for a smaller practice set. Do not describe it as faster than its simpler baseline. Repeat on the demonstration machine with `/evidence` and retain the new exports.

## Explicitly not verified live

- Gemini generation against the real provider: the posted credential was not copied into source; a rotated replacement must be configured locally. Offline transport/schema validation does not establish answer quality.
- Hosted Judge0 execution: no hosted runner key was supplied. Local adapter-contract tests validate request/response behavior and privacy, not the live provider's availability or sandbox.
- SMTP email delivery: requires a running Mailpit instance or configured SMTP service.
- Public LeetCode availability: endpoint access and profile data depend on the upstream service and network. Its cached/unavailable path is implemented; imported data is separate from native solved credit.
- Docker/PostgreSQL container startup: the local Docker Desktop Linux engine was not running. Configuration syntax was validated; the native app was tested using its persistent H2 profile.
- CI execution on GitHub: the initial remote job did not start because of a GitHub account-level restriction; no build/test steps ran. Resolve the repository owner's account configuration and rerun before claiming remote CI validation. See [the handoff guide](HANDOFF.md) for the recorded diagnostic.

## Reproduce

Use the README setup, then run `mvn -f backend/pom.xml test`, `npm test`, `npm run build`, `python scripts/verify_api.py --export`, and `npm run test:e2e`. Browser screenshots are regenerated under `.impeccable/review` and excluded from Git. The validation date and results above describe this run only.
