# 1on1 revamp in the datalis visual language — design

## Intent

The owner wants 1on1 to look and work like their other product, datalis.in (Deku Finance): light, calm, premium,
keyboard-first, with the product itself shown on the landing page. Every area of the app is revisited so that nothing
reads as "a dump of text", and the home page tells a learner what to do next. Approved 2026-11-18 ("do it all";
datalis is the owner's own project, so its design system is reused directly).

## Visual system (from datalis.in's live tokens)

| Token | Value |
| --- | --- |
| Font | Geist (sans) and Geist Mono, everywhere; no serif display face |
| Background | `#f4f6f5`; surfaces `#fff` |
| Borders | `#e3e9e6`, strong `#d2dad7` |
| Text | main `#0e1b19`, muted `#5e6e6a`, subtle `#9aa7a3` |
| Accent | teal `#05b8a5`, hover `#04a594`, wash `#05b8a51f`, active row `#05b8a514`, aqua `#a5e9de` |
| Dark panels | obsidian `#0c1715`, charcoal `#13211f`, slate `#2c3c39` |
| Shape | buttons 9 px radius, cards 12 px, focus ring `0 0 0 2px #05b8a5d9` |

- **Light only.** The theme toggle and dark tokens are removed.
- The six algorithm-family colours stay (they carry meaning in lessons and traces), tuned to sit beside the teal.
- Keyboard-first: "Jump to… Ctrl K" in the top bar; single-key shortcuts to main areas shown beside sidebar items; a
  shortcut strip on wide screens.

## Order of work (each phase is planned, built test-first, reviewed and shown)

1. **A. Look and shell + landing.** Tokens, fonts, light only, shell with shortcut hints and keyboard navigation, and a
   datalis-style landing page that shows real 1on1 fragments (an animation, a sheet row with "Asked at", a drill being
   checked, contests, the key map, learning paths).
2. **B. Home.** "What to do next", activity (streak, this week), what's happening (upcoming contests), and recently
   reported questions; plus "I was asked this" reports from learners (owned, fresh company data).
3. **C. Explore.** Lesson page as clear steps with no empty gaps; working filters; concept map in order; learning paths
   as visual steps; animations page polish; the performance lab is removed.
4. **D. Practice.** Topic filters for 1on1 problems; rebuilt bank UI; mock OA as a timed quiz (MCQ from Prep pools plus
   coding); contests.
5. **E. Prep.** Each guide becomes tabs: Notes, Quiz, Sources (references), and a printable PDF.
6. **F. Plan, notebook, progress, study together.** AI plan via Gemini when a key is set, with a deterministic planner
   as the fallback; notebook and progress show what was done and where the learner is heading.
7. **G. Missing DSA concepts.** Union-find, topological sort, minimum spanning trees, Bellman-Ford and Floyd–Warshall,
   segment and Fenwick trees, greedy, bit manipulation, KMP and rolling hash, monotonic stack and queue, knapsack, LCS
   and interval DP. Every new concept gets a full step-by-step trace animation like the existing 33 (owner's decision,
   2026-11-18), with the engine's models extended where the array, graph and table views do not fit.

## Constraints

- Problem statements from other platforms are never copied; "solve here" keeps working with the learner's own input.
- No licensed source of 2026 company tags exists; fresh company data comes from learners' own reports, labelled as such.
- AI features say when they are unavailable and never award credit.
- Additive migrations only; existing learner data is preserved. Works at 390 px; accessible.
