# Representative contract fixtures

Captured from the native Java API on 16 November 2026. Each `*.trace.v2.json` is a complete trace for its lesson's default scene, not an AI-generated explanation or an own-code runtime trace. These files contain public authored inputs only.

- Sliding window: duplicate values with distinct entity IDs and window state.
- BST: stable node identity and structural insertion snapshots.
- BFS: directed edges, current/discovered vertices and ordered frontier.
- Tabulation: destination/dependency values and synchronized code lines.
- `sliding-window.lesson.public.json`: sanitized public lesson blocks and four challenge definitions. Gold grading rules are absent.

Java DTOs are in `Contracts.java`; frontend types are in `src/types.ts`. See [API.md](../API.md) for attempts, saved context, conversations and durable job semantics. Fixture field order is not contractual. Preserve semantic fields and version changes explicitly when refining the UI.
