# Phase 1 handoff — 16 November 2026

**Later curriculum checkpoint:** the owner brought curriculum content forward. Start with [CURRICULUM.md](CURRICULUM.md) and [CURRICULUM_VALIDATION.md](CURRICULUM_VALIDATION.md) for the current 24 concepts / 33 notebooks. This Phase 1 record and its bundle describe the earlier foundation; its test counts/catalogue counts are historical. Practice and UI/UX remain Phase 2; the skill-tree UI is undecided.

**Delivered:** the native application foundation and four expanded reference journeys. **Open gate:** actual Judge0 execution under Docker Desktop. Phase 1 must not be presented as fully accepted until that gate passes. Phases 2 and 3 remain assigned to the two incoming teammates in [the approved plan](IMPLEMENTATION_PLAN.md).

No push or public deployment has been performed. Existing documentation changes were retained. The source checkpoint is a foundation checkpoint, not a declaration that every feature in [FEATURES.md](FEATURES.md) is finished.

## Incoming owner's setup

Prerequisites: Node 22.14+, npm, Java 21+, Maven 3.9+, Docker Desktop with its Linux engine. Python 3 is needed for content/HTTP/reference scripts; optional g++ verifies trusted C++ references. The observed development machine uses Windows 11, Node 22.14, Java 25.0.4.1 compiling for release 21, Maven 3.9.14 and Python 3.13. Other OS implementations are provided but not yet rehearsed.

```sh
# When receiving the bundle, clone it into a new, empty destination:
git clone --branch main /path/to/1on1-phase1.bundle 1on1
cd 1on1
npm run setup
npm run doctor
```

`setup` creates `.env` only if missing, preserves existing data/configuration, installs locked dependencies and compiles Java. It creates random local runner/database/Redis secrets in ignored `.cache/local.env` and a managed `.cache/judge0.conf`. Repeat setup safely; do not transfer another learner's secrets or database. JDK discovery changes only child process environment, never machine Java/PATH.

Configure `GEMINI_API_KEY` locally; keep it out of Git, chat and `VITE_` variables. The default `gemini-3.1-flash-lite` was verified through the application. A previously exposed key should be rotated by its owner. A missing key leaves deterministic lessons usable.

```sh
npm run dev           # both app servers plus Docker services
npm run stop          # stop owned app processes/containers; retain data
npm run verify        # Java tests, frontend tests, production build
npm run verify:references  # trusted authored Python/C++ references
npm run test:e2e      # app must be running; install Playwright Chromium first
npm run verify:live   # actual Judge0 + Gemini; blocked checks fail the command
npm run backup       # Java must be stopped
```

Web: `http://127.0.0.1:5173`; Java: 8080; Judge0: 2358; Mailpit UI: 8025; SMTP: 1025. App data: `backend/.data`. The primary `infra/local.compose.yaml` contains Judge0/worker, private runner PostgreSQL/Redis and Mailpit; it does not containerize the app. `compose.yaml` is an older optional full-app topology, with different networking and no included judge; it remains unverified.

While the runner blocker remains, explicitly use `npm run dev:core` and `npm run stop:core`. These aliases avoid PowerShell/npm argument-forwarding differences. This permits learning verification but is not a grading workaround. A configured token is not proof of runner readiness. `doctor` reports service failures separately; its exit status concerns the core native prerequisites.

## Exact runner blocker

Docker Desktop initially reported engine 27.5.1, Linux x86_64 and cgroup v2, with about 4 GB allocated RAM. Pulling the upstream `judge0/judge0:1.13.1` image failed with **unexpected EOF**. After one retry the daemon stopped responding even to container listing. The backend log at `%LOCALAPPDATA%/Docker/log/host/com.docker.backend.exe.log` reported:

```text
sd 0:0:0:4: Device offlined - not ready after error recovery
SUBSYSTEM=scsi
```

The observed failure is Docker/WSL virtual-device I/O during image acquisition; Judge0 sandbox execution and cgroup compatibility have not been reached/proven. The owner was asked to restart Docker Desktop. No destructive disk/volume cleanup, VM replacement, hosted judge subscription or fallback was performed.

After the owner restores the Linux engine:

1. Run `npm run doctor` and confirm engine responsiveness and adequate resources.
2. Run `npm run services`; inspect `docker compose --env-file .cache/local.env -f infra/local.compose.yaml logs --tail=100 judge judge-worker` locally. Do not publish logs/configuration containing tokens.
3. Run the app and use Settings → runner check. Language discovery must find all three installed runtimes.
4. Run `npm run verify:live` and perform the browser coding flow. It verifies the eight authored references in Java/Python/C++, bad executions and hidden-data redaction; it also calls actual Gemini explanation, visualization and streaming.
5. Verify a known receipt across Java restart, custom-run exclusion, repeated acceptance, wrong output, compilation error, timeout and service outage. Contract tests already cover these adapter semantics; an actual sandbox run remains necessary.
6. Test Mailpit reset-email delivery and inspect compatibility before claiming the full gate. If Docker Desktop cannot support the upstream isolation requirements, record the exact result and seek an explicit owner decision; do not quietly switch environment.

## Module and contract map

| Area | Implementation / extension point |
| --- | --- |
| Authoritative traces | `TraceEngine`, typed `Contracts.ExecutionTrace` version 2, stable entities/operations/tree nodes/links; seed preserved. |
| Playback/rendering | `Experiment`, `experiment/usePlayback`, `SceneCanvas`; legacy renderer retained for later catalogue refinement. |
| Lessons/challenges | `scripts/reference_content.py` and generated `content.json`; `ChallengeService`, `StudyController`, `ChallengeCard`. Never publish private rules. |
| Study persistence | StudyContext v1 stores full scene/seed/step/section; drafts include source hash. Private conversations restore per lesson/problem. |
| Evidence/progress | `ProgressService`; additive V2 attempts/events/solved-credit tables. Autosaves create no activity. |
| Durable execution | `ExecutionService` + `JudgeClient`; persisted source/fixtures/receipts, bounded queue, recovery/idempotency and explicit interruption. |
| Tutoring | `TutorService`, thin controller, canonical `teaching-policy.md`; Gemini system instruction, SSE, Java-validated scenes and readiness. |
| Setup/operations | `scripts/project.mjs`, local compose, `.env.example`; no global setup mutation. |

Keep Java DTOs, `src/types.ts`, [API.md](API.md) and [fixtures](contracts/README.md) aligned. V2 migration adds evidence tables without modifying V1 or resetting documents/accounts. Seed updates preserve administrator-edited content. Existing H2 reopened at schema version 2 successfully; PostgreSQL rehearsal remains outstanding. Sessions are process-local, so sign in again after Java restarts.

## Reference journey smoke test

Create a separate test account. Development also provides `demo@1on1.local` / `learnwith1on1`, with no fake achievements; it is not a production account.

1. Open sliding window, BST, BFS and tabulation; inspect the mental model, worked example, minimal implementation, invariant and mistakes.
2. Predict, identify the pattern, manipulate input and complete the dry-run table. Verify Java feedback and signed-in persisted attempts. Guests may try grading without saved credit.
3. Change an experiment input, seek to a step, save a note and reload. Input, seed and exact step should restore without activity inflation.
4. Ask a contextual Gemini question, stop a response, generate a supported experiment, save an explanation and reopen the conversation.
5. Open either linked problem, change language, edit/save source and reopen it. Once Judge0 is ready, run and submit real code; only official acceptance awards a unique solved credit.
6. Check mobile/local diagram scrolling, dark theme, keyboard arrows/Space/Home, reduced motion and failure retry.

The eight linked problems have three-language references and adversarial/boundary fixtures. The remaining 52 currently have Java references; the UI labels that fallback accurately. All 24 lessons have server-graded legacy checkpoints, but the other 20 lessons do not yet match the four reference journeys' depth.

## Observed verification

| Check | Observed result |
| --- | --- |
| Java | 49 JUnit tests, zero failures/errors; algorithms, all 24 typed traces, boundary inputs, challenge grading/privacy, events, stable identities and durable adapter recovery. |
| Java references | All 60 compiled references pass 442 fixtures inside ContentTest. |
| Python/C++ references | Eight of each, 78 fixture executions per language; local trusted-source verification only. Windows compiler support uses child-only PATH entries. |
| Frontend | Nine transport/playback unit tests and production build pass. Monaco remains a large lazy-loaded bundle and produces a Vite size warning. |
| Browser | 12 scenarios pass: original flows, four reference lessons, saved inputs/steps, activity exclusion, rapid seek, reduced motion, theme/widths and tutor history retry/isolation by context. |
| Real HTTP | Sessions/CSRF, content privacy, persistence, plans, permissions, three evidence methods and logout pass. |
| Actual Gemini | Explanation, validated scene and real SSE pass through Java with the locally configured credential. |
| Actual Judge0 | Blocked: language discovery cannot reach the local runner. No real acceptance claimed. |
| Persistence/backup | Existing H2 version 2 reopened; stopped H2 copied by backup command and reopened without reset. |
| Fresh source setup | Source-only bundle restore, setup/doctor, fresh V1→V2 database, 12 browser journeys and expanded draft-switch follow-up pass. Repeated setup preserved config/secrets/database byte-for-byte. See [VALIDATION.md](VALIDATION.md); fresh-machine/Docker gates remain open. |
| Other integrations | SMTP, PostgreSQL and LeetCode live checks remain open. Remote GitHub CI has not run because of the previously recorded account restriction. |

Portable core-only commands were added after the rehearsal exposed PowerShell flag forwarding. The final handover bundle uses an explicit main branch, excludes personal/generated files, and is verified by Git.

Detailed local logs and live evidence are under ignored `.cache`, while screenshots are under ignored `.impeccable/review`. The committed validation record preserves results without personal databases or test accounts. Tests deliberately using a local provider fixture are not live-service evidence.

## Specific Phase 2 backlog

Start by reproducing the smoke test and closing the runner gate. Then:

1. Use the four reference lessons and contracts to expand the other 20 lessons. Add two substantive checkpoints and a pattern drill per lesson, dry-run variants per family, and meaningful animations instead of generic highlight changes.
2. Bring the remaining 52 problems to three-language reference quality, replace generic hints/editorials, and add per-problem adversarial tests. Extend admin forms/publication validation to these typed lesson/challenge fields rather than editing raw JSON indefinitely.
3. Build the free concept map/list and evidence-based next action. Preserve the distinction between exploration, challenge success and accepted code; do not convert autosaves into mastery.
4. Add dated plan tasks, rescheduling/completion-preserving regeneration and persisted review scheduling (1/3/7 days after success; next day after a miss). Hint use and recency become explicit evidence.
5. Evolve the current tutor trigger into the Blob, keeping cancel/retry/context/history; add graduated contextual actions and subtle motion.
6. Implement owned PDFBox extraction and Lucene BM25 notebook search: text PDF 10 MB/100 pages, page citations, selected-source retrieval, deletion/isolation, editable cards and unsupported-file feedback. Current note storage is not RAG.
7. Refine layout, motion and mobile interaction across the full product, then repeat the Phase 2 exit gate. Keep playback/Java contracts stable.

Own-code tracing, student performance experiments, MCP pairing/client verification and three refined external skills remain Phase 3. The current teaching policy is preparation, not a shipped integration.

## Transfer and attribution

Use the local `phase1-foundation` checkpoint/tag and `1on1-phase1.bundle` supplied by the outgoing owner. Verify it with `git bundle verify`, clone to a fresh directory, configure your own credentials and run setup/doctor/tests. The bundle contains source history, not `.env`, `.cache`, databases, uploads, dependencies or generated output. Keep personal backups separate.

Resolve undocumented setup failures before new development. Add an additive migration for schema changes; never edit applied V1/V2 or reset a learner's DB. Each incoming teammate records their own implementation and understands the assessed Java trie, greedy set cover and randomized Quickselect. Do not invent contribution records or describe Codex-assisted code as independently authored student work.
