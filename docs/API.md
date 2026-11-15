# Java API contracts

Base URL: `/api/v1`, same-origin through Vite/Nginx. JSON request/response bodies; UTF-8. Server-session cookie authentication. Fetch `GET /auth/session` and send its `csrf` value in `X-CSRF-TOKEN` on every mutation. Anonymous experiments also require CSRF. Browser code must never receive provider credentials.

Errors use `{ "message": "Readable recovery guidance" }`: 400 invalid input, 401 sign-in required, 403 CSRF/role failure, 404 unavailable owned item, 429 usage limit, 503 missing/busy service, 502 external-service failure. Ownership is checked server-side. See `src/types.ts` for frontend interfaces.

## Accounts

| Method/path | Input/result |
| --- | --- |
| GET `/auth/session` | `{user: {id,name,email,role} or null, csrf}` |
| POST `/auth/register` | `{name,email,password}`; student account and session |
| POST `/auth/login` | `{email,password}`; account and renewed session identifier |
| POST `/auth/logout` | Invalidates the session |
| POST `/auth/request-reset` | `{email}`; generic delivery acknowledgement |
| POST `/auth/reset-password` | `{token,password}`; consumes an unexpired token |
| GET `/system` | AI/execution configuration booleans, provider/model labels; no keys |

Passwords must be 8–72 characters. The SMTP reset token is SHA-256 hashed at rest and expires after 30 minutes. The bootstrap administrator uses separate server configuration and a minimum 12-character password.

## Public learning content and experiments

- GET `/lessons`, `/lessons/{id}`: published structured lessons. Each has an experiment, authored pseudocode, complexity, checkpoint and topic metadata.
- GET `/paths`: ordered lesson ID collections.
- GET `/problems`, `/problems/{id}`: published statements, samples, constraints, topics and hints. Hidden tests/reference source are stripped from these responses.
- GET `/problems/{id}/editorial`: explicitly requested editorial/reference source.
- GET `/search?q=prefix`: up to 20 unique public results through the cached Java trie, case-insensitive trimmed prefix semantics. Maximum 100 query characters.
- POST `/experiments`: `SceneRequest` below; returns a versioned Java trace. No authentication is required to try a lesson.

```json
{"algorithm":"sliding-window","input":"2, 1, 5, 1, 3, 2","target":3,"words":""}
```

`ExecutionTrace` contains `version`, `algorithm`, `family`, `input`, `steps`, and `result`. A step contains `id`, independent `array`, `active` positions, `variables`, `text`, and zero-based authored pseudocode `line`. Tree/graph/trie scenes add typed geometry/state data. Inputs allow 1–32 integers in -10000..10000. Search/pair targets can be negative. Window sizes and one-based selection ranks must be valid for the input. Factorial/table limits are explicit; words are capped at 200 characters. Graphs are small generated teaching networks, not an arbitrary graph-upload format.

## Authenticated learning state

- GET `/progress`: complete defaults plus completed lessons, native solved problems, bookmarks, activity, checkpoints, preferences, resume position, notes, plans, drafts and visible submissions.
- POST `/progress`: updates completion/bookmarks/preferences/resume, or `{checkpoint:{lesson,answer}}`. Clients cannot assign native solved credit.
- GET/POST `/notes`: list or create/update owned thoughts. Fields: `title`, `text`, `lesson`, optional `id`, `reviewed`, validated `experiment`. Text: 1–20000 characters.
- DELETE `/notes/{id}`: removes an owned note.
- PUT `/drafts/{problem}`: `{language,code}`; one owned draft per problem/language.
- POST `/plans`: `{title,topics,difficulty,perDay}`; returns selected `{id,adds}` entries, uncovered topics, grouping and method. Requires 1–50 topic names. Difficulty is `All`, `Easy`, `Medium` or `Hard`.

## Judge boundary

POST `/submissions`:

```json
{"problem":"problem-running-altitude","language":"java","code":"...student source...","official":true,"input":""}
```

Returns a persistent job snapshot. Poll GET `/submissions/{id}` while `QUEUED`/`RUNNING`. Terminal states include `ACCEPTED`, `WRONG_ANSWER`, `COMPILATION_ERROR`, `TIME_LIMIT`, `RUNTIME_ERROR`, `FINISHED` (custom run), and `UNAVAILABLE`. Supported language keys: `java`, `python`, `cpp`. Source limit: 50000 characters; custom input: 10000. Official fixtures remain private. Public results can include input/expected/actual; hidden results omit them. Judge tokens are never returned. Only official acceptance updates a unique native solved-problem set.

## Gemini boundary

- POST `/tutor`: `{message,mode:"visualize",lesson?,experiment?,step?,code?,submission?,history?}`. Returns `{text,scene}` after schema/business validation.
- POST `/tutor/stream`: same context with normal explanation mode. Returns SSE events `token` (`{text}`), `done` (`{ok:true}`), or `error` (`{message}`). Text tokens are provider-generated, not an artificial playback of a complete answer.

Message length is capped at 8000; code fragments at 20000; recent conversation at eight bounded messages. A selected experiment is recomputed by Java before its step is included. Lesson context must be public; submission context must belong to the requester. Hidden input/expected data is never included.

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
