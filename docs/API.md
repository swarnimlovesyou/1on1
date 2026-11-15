# Java API contracts

Base URL: `/api/v1`, same-origin through Vite/Nginx. JSON request/response bodies; UTF-8. Server-session cookie authentication. Fetch `GET /auth/session` and send its `csrf` value in `X-CSRF-TOKEN` on every mutation. Anonymous experiments also require CSRF. Browser code must never receive provider credentials.

Errors use `{ "message": "Readable recovery guidance" }`: 400 invalid input, 401 sign-in required, 403 CSRF/role failure, 404 unavailable owned item, 429 usage limit, 503 missing/busy service, 502 external-service failure. Ownership is checked server-side. See `src/types.ts` for frontend interfaces.

Phase 1 contracts are defined in `backend/src/main/java/com/oneonone/Contracts.java`, TypeScript types, the tests and [representative fixtures](contracts/README.md). A reused idempotency key with different content returns 409.

## Accounts

| Method/path | Input/result |
| --- | --- |
| GET `/auth/session` | `{user: {id,name,email,role} or null, csrf}` |
| POST `/auth/register` | `{name,email,password}`; student account and session |
| POST `/auth/login` | `{email,password}`; account and renewed session identifier |
| POST `/auth/logout` | Invalidates the session |
| POST `/auth/request-reset` | `{email}`; generic delivery acknowledgement |
| POST `/auth/reset-password` | `{token,password}`; consumes an unexpired token |
| GET `/system` | Compatibility configuration booleans plus `aiStatus` and `executionStatus`; no keys |
| POST `/system/check` | Authenticated runner language-discovery probe; does not claim successful code execution |

Passwords must be 8–72 characters. The SMTP reset token is SHA-256 hashed at rest and expires after 30 minutes. The bootstrap administrator uses separate server configuration and a minimum 12-character password.

## Public learning content and experiments

- GET `/lessons`, `/lessons/{id}`: published structured lessons. Each has an experiment, authored pseudocode, complexity, checkpoint and topic metadata. The four reference lessons add typed teaching `blocks`, `challenges` and two related problems. Initial public responses omit gold answers, private rules and post-attempt explanations.
- GET `/paths`: ordered lesson ID collections.
- GET `/problems`, `/problems/{id}`: published statements, samples, constraints, topics and hints. Hidden tests/reference source are stripped from these responses.
- GET `/problems/{id}/editorial`: explicitly requested editorial/reference source.
- GET `/search?q=prefix`: up to 20 unique public results through the cached Java trie, case-insensitive trimmed prefix semantics. Maximum 100 query characters.
- POST `/experiments`: `SceneRequest` below; returns a versioned Java trace. No authentication is required to try a lesson.

```json
{"algorithm":"sliding-window","input":"2, 1, 5, 1, 3, 2","target":3,"words":"","seed":42}
```

`ExecutionTrace` version **2** contains `algorithm`, `family`, normalized complete `input`, `steps`, and `result`. A step contains `id`, independent `array`, stable `entities` (`id`, `value`, `position`, `role`), `active` positions, `variables`, `text`, zero-based authored pseudocode `line`, and semantic `operation` (`kind`, `entityIds`, `details`). Tree nodes carry stable IDs; graphs expose edges/activeEdge; linked structures expose links/head. Renderers use IDs, not values or current positions, for object identity. Java owns snapshots. `result` is the final step; the bound is 1,000 authored steps, distinct from Phase 3 runtime tracing.

Inputs allow 1–32 integers in -10000..10000. Search/pair targets can be negative. Window sizes and one-based selection ranks must fit the input. Factorial is bounded to 10 and Fibonacci tables to 16. Words are capped at 200 characters. Graphs are small generated teaching networks, not arbitrary graph uploads. BST duplicate keys are ignored. Save normalized input and seed for reproducibility.

## Authenticated learning state

- GET `/progress`: defaults, explored lessons (`completed` legacy name), native solved problems, bookmarks, validated `activity`, private attempt summaries, `studyContexts`, preferences, resume, notes, plans, drafts and visible submissions. Historical activity remains under `legacyActivity`; it is not relabelled as new evidence.
- POST `/progress`: updates completion/bookmarks/preferences/resume, or `{checkpoint:{lesson,answer}}`. Clients cannot assign native solved credit.
- GET/POST `/notes`: list or create/update owned thoughts. Fields: `title`, `text`, `lesson`, optional `id`, `reviewed`, validated `experiment`. Text: 1–20000 characters.
- DELETE `/notes/{id}`: removes an owned note.
- PUT `/drafts/{problem}`: `{language,code}`; one owned draft per problem/language. Returned `codeRevision` is SHA-256 of language + newline + source.
- POST `/plans`: `{title,topics,difficulty,perDay}`; returns selected `{id,adds}` entries, uncovered topics, grouping and method. Requires 1–50 topic names. Difficulty is `All`, `Easy`, `Medium` or `Hard`.

## Judge boundary

POST `/submissions`:

```json
{"requestId":"client-generated-uuid","problem":"problem-running-altitude","language":"java","code":"...student source...","official":true,"input":""}
```

Returns a persistent job snapshot. Poll GET `/submissions/{id}` while `QUEUED`/`RUNNING`. Terminal states include `ACCEPTED`, `WRONG_ANSWER`, `COMPILATION_ERROR`, `TIME_LIMIT`, `RUNTIME_ERROR`, `FINISHED` (successful custom run), `INTERRUPTED`, and `UNAVAILABLE`. Supported language keys: `java`, `python`, `cpp`; installed IDs are discovered at runtime. Source limit: 50000 characters; custom input: 10000. Official fixtures remain private. Public results may include input/expected/actual; hidden results omit them. Tokens, fixture snapshots and dispatch internals are never returned.

Source/fixtures/receipt tokens/results/deadline are persisted before/after runner calls. On restart, known receipts are polled; an uncertain POST without a saved receipt is marked interrupted, never blindly resubmitted. Jobs expire after 300 seconds. Two workers and a queue of 20 bound local work. Only official acceptance inserts unique `(member,problem)` credit and a validated event; duplicate acceptance and custom runs never increase it. Contract tests establish these semantics; live Docker grading remains blocked.

`self-hosted` sends only `X-Auth-Token`; explicit `rapidapi` sends its key/host headers. The Java host never runs student source as an ordinary subprocess. Resource requests disable network and bound CPU, wall time, memory and output; the local Judge0 configuration also prohibits enabling network/callbacks/additional files.

## Gemini boundary

- POST `/tutor`: `{message,mode:"visualize",lesson?,experiment?,step?,code?,submission?,history?}`. Returns `{text,scene}` after schema/business validation.
- POST `/tutor/stream`: same context with normal explanation mode. Returns SSE events `token` (`{text}`), `done` (`{ok:true}`), or `error` (`{message}`). Text tokens are provider-generated, not an artificial playback of a complete answer.

Message length is capped at 8000; code fragments at 20000; recent conversation at eight bounded messages. A selected experiment is recomputed by Java before its step is included. Lesson context must be public; submission context must belong to the requester. Hidden input/expected data is never included.

The canonical teaching policy lives in `backend/src/main/resources/teaching-policy.md`, supplied as the provider system instruction. It guides graduated hints and exam explanations. It is not an installed external-assistant skill or MCP server; those are Phase 3. Readiness records actual successful calls separately from key presence. The configured default is `gemini-3.1-flash-lite`; models remain locally configurable.

GET/PUT `/conversations/{context}` stores the current learner's last 20 messages (120000 total serialized characters). Roles are `you`/`tutor`; text is capped at 16000 per message. Optional scenes must validate on Java. Context is a lesson/problem ID or `workspace`; records are private and produce no achievement events. Client history-load failures have explicit retry; streaming supports cancellation.

## Challenges and saved context

POST `/challenges/{id}/attempts` accepts `{answer,requestId}` and returns typed `{id,challengeId,kind,correct,feedback,explanation,saved}`. CSRF is mandatory; guests receive grading with `saved:false`, while signed-in attempts are persisted/idempotent by `(member,requestId)`. Public challenge definitions include prompt, options/fields and input metadata, never private grading rules.

| Kind | Answer | Java check |
| --- | --- | --- |
| prediction / pattern | Integer option index | Private authored valid answer |
| manipulation | Full scene request | Recompute trace and compare the authored state condition |
| dry-run | Object keyed by authored field IDs | Recompute the specified trace step, compare requested fields and report the first error |

The four reference lessons demonstrate each kind; legacy checkpoint grading uses the same service. A successful challenge is evidence of that challenge, not automatic problem acceptance. Alternative valid scenes for a manipulation condition can pass; Phase 2 expands dry-run variants.

GET/PUT `/study-context/{lesson}` is owned. PUT example:

```json
{"version":1,"lesson":"lesson-sliding-window","scene":{"algorithm":"sliding-window","input":"4,4,4,1","target":3,"words":"","seed":42},"step":3,"section":"experiment","codeRevision":""}
```

Lesson/algorithm must match, the step must exist, and section/revision sizes are bounded. Java saves complete scene/location and updates compatibility resume fields. Lesson-only contexts have an empty code revision; code drafts expose their actual revision. Autosaves, notes, drafts and conversations do not create study activity. Exploration is recorded on explicit lesson completion; signed-in graded attempts and unique acceptance create validated events.

## Migrations and compatibility

V1 remains unchanged. Additive V2 introduces `challenge_attempts`, `learning_events` and `solved_credits`; existing documents/accounts are retained. Previously recorded native solved state is merged into the summary; new credit uses the ledger. Do not edit an applied migration. Admin-edited content is preserved by the seed loader. PostgreSQL remains supported in schema/configuration, with a live compatibility rehearsal still outstanding.

## Cohorts and external profiles

- GET/POST `/cohorts`: joined groups or `{name}` to create a private invitation.
- POST `/cohorts/join`: `{code}`.
- GET `/cohorts/summary`: member-visible metadata and quartile thresholds, computed independently without sorting a leaderboard. Fewer than five members yields no thresholds.
- GET/POST/DELETE `/connections/leetcode`: read cached record, refresh `{username}`, or disconnect. Cache includes `status`, `attemptedAt`, optional `syncedAt`, `data` and readable failure message. Same-profile manual refresh has a 15-minute cooldown; scheduled refresh runs every six hours. The endpoint is unofficial and recent accepted history is limited.

## Evidence and administration

- POST `/evidence`: `{method:"trie"|"set-cover"|"quickselect"}`; returns three increasing sizes, mean algorithm/baseline times, quality data where relevant, seed, warm-up/repetition counts and machine metadata.
- ADMIN GET `/admin/content`: authored records and daily usage totals.
- ADMIN POST `/admin/content`: stable `id`, matching `kind` (`lesson`, `problem`, `path`), title and type-specific fields. Problem publication requires 5–20 fixtures, editorial and reference. Lessons require a valid experiment and checkpoint.
- ADMIN POST `/admin/import`: up to 100 structured records. Use the editor's JSON file import/paste workflow. Records are validated individually; earlier successful records are not rolled back if a later record fails, so correct and retry failed records by stable ID.
