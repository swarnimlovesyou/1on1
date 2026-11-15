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
- CI execution on GitHub: the workflow is checked in; its remote result must be confirmed after push.

## Reproduce

Use the README setup, then run `mvn -f backend/pom.xml test`, `npm test`, `npm run build`, `python scripts/verify_api.py --export`, and `npm run test:e2e`. Browser screenshots are regenerated under `.impeccable/review` and excluded from Git. The validation date and results above describe this run only.
