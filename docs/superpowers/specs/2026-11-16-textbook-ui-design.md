# Premium UI: "textbook, beautifully printed" — design

## Intent

Make 1on1 feel premium for the final DSA project: crafted and calm, like a well-printed computer science book, with the
algorithm animations as the signature element. The owner chose direction A from three mockups (textbook, instrument
panel, engineering notebook). Who it must impress most (the evaluators at the demo, or students day to day) was not
answered. This design assumes both, keeping showpiece moments to the landing hero and the lesson animation.

## Goals

- **A consistent new visual system on every page:** paper colours, serif display type, a readable text face, and one
  colour per algorithm family.
- **A deeper treatment of the screens a demo shows:** landing page, home, concept library, lesson page and problem page.
- **Recognisable families:** each algorithm family (searching, structures, trees, graphs and so on) has a colour and a
  small mark, used the same way in the library, concept map, lesson header, trace highlight and practice list.
- **Readable lessons:** long prose sits at about 65 characters per line in the text face, with generous margins and a
  quiet chapter outline.

## Non-goals

- No change to features, routes, APIs, data or copy beyond small label tweaks the layout needs.
- No new illustration set or animation library.
- No redesign of the trace engine's visual models beyond colour and type.

## Anti-goals (a failure even if it technically works)

- **A cream-and-terracotta template:** the accent comes from the family colours, not a single warm clay.
- **Lower contrast or readability than today:** body text must meet WCAG AA in both themes.
- **A broken dark mode, or one that's merely inverted:** night reading gets its own palette.
- **Regressions in the browser suite,** including phone width, keyboard and reduced motion.

## Constraints

- Local-first, so fonts ship with the app through `@fontsource` packages, as Geist does today, never from a CDN at
  runtime.
- The existing theme switch (light, dark, system via `data-theme`) stays.
- The experiment components read colours from CSS tokens, so they must keep working through tokens alone.
- Accessibility: visible focus, reduced motion respected, no horizontal scroll at 390 px.

## Approaches considered

| Direction | Trade-off | Chosen |
| --- | --- | --- |
| A. Textbook, beautifully printed | Calm and crafted; best for reading-heavy lessons; family colours give identity | **Yes** |
| B. Instrument panel | Fast and dense; colder for beginners; closest to today's generic dark look | No |
| C. Engineering notebook | Most distinctive; hardest to keep uncluttered on phones | No |

The build approach is my call: change the tokens and type first, so every page moves at once, then restyle the five key
screens. Restyling page by page would leave the app half old and half new for longer.

## The system (my calls, open to correction)

**Type**
- Display: Fraunces (400/500) for page and lesson titles and large numbers.
- Text: Source Serif 4 (400) for lesson prose and editorials.
- Interface: Inter Tight (400/500) for navigation, buttons, labels and forms.
- Code and trace values: JetBrains Mono, kept.
- Scale: 12 / 13 / 15 / 17 / 22 / 30 / 40. Prose at 17 px with line-height 1.75.

**Paper (light, the default)**

| Role | Colour |
| --- | --- |
| Page | `#FBFAF7` |
| Raised surface | `#FFFFFF` |
| Soft surface | `#F1EEE6` |
| Ink | `#1F2430` |
| Muted | `#5E6370` |
| Rule | `#E7E3DA` |

**Night (dark)**

| Role | Colour |
| --- | --- |
| Page | `#17181B` |
| Surface | `#1E2024` |
| Soft surface | `#25282D` |
| Ink | `#ECE8DF` |
| Muted | `#A39F96` |
| Rule | `#33363C` |

**Family colours** (light / night; each with a soft wash for backgrounds)

| Family | Concepts | Colour |
| --- | --- | --- |
| Foundations | complexity, arrays, strings, hashing | slate `#3F5873` / `#9DB4CC` |
| Searching and sorting | sorting, prefix sums, two pointers, windows, binary search, intervals | green `#2E6B5E` / `#7CC2B0` |
| Linear structures | matrices, linked lists, stacks, queues | ochre `#8A5A12` / `#E0B465` |
| Recursion and DP | recursion, backtracking, dynamic programming | plum `#6B3F73` / `#C79BD0` |
| Trees and heaps | binary trees, BST, heaps | rust `#94431F` / `#E59A74` |
| Graphs | graph representation, BFS, DFS | blue `#2F55A4` / `#8EAEF0` |

**Family mapping** (my call; a frontend topic-to-family table, because lessons and problems have no family field and
data changes are out of scope):

| Item | Family |
| --- | --- |
| AVL | Trees and heaps |
| Trie | Trees and heaps (a trie is a tree) |
| Dijkstra, max flow | Graphs |
| Quickselect | Searching and sorting (it partitions like quicksort) |
| Bloom filter, set cover | Foundations (both build on hashing and sets) |

A problem takes the family of its first topic that maps, and falls back to Foundations.

**Colour roles** (my call; the current single `--accent`, used about 165 times, splits three ways):
- **Interface:** primary buttons and links are ink. Focus rings, selection, active tabs, input focus and progress lines
  use a deep ink-blue: `#2F4A6E` on paper, `#A9BEDC` at night. Active and selected states stay clearly visible in both
  themes.
- **Subject:** the family colour, only where the subject is that family: marks, lesson header, trace highlight.
- **State:** success, warning and error keep their meanings: accepted, review due, failed.

Learning-path markers (blue, green and orange today) become neutral, so they aren't mistaken for families.

**Shape and depth**
- Radius 10 px for cards and 6 px for controls.
- Hairline rules instead of shadows; one soft shadow kept for popovers and the tutor drawer.

## Screens

- **Landing:** keep today's structure and copy. The hero uses the Fraunces headline, with its live trace in the
  searching family's green on the soft surface. The 1/2/3 story steps and the concept and problem counts stay,
  restyled.
- **Home:** next action and reviews as a calm reading column, with family marks on each item.
- **Library and concept map:** library rows grouped by family, each with its mark. Map nodes keep their progress
  colours (explored, passed, accepted, review due), because each grade is separate evidence. The family appears as a
  small dot on each node.
- **Lesson:** the family label and Fraunces title open the page. The animation is the hero, framed on the soft surface.
  Prose sits in the serif text face at about 65 characters. The chapter outline stays in the left margin, and practice
  sections are separated by rules, not boxes.
- **Problem:** the statement and editorial in the serif text face, the Coach and hints in the interface face. The
  Monaco editor doesn't read CSS variables, so it gets its own paper and night themes.
- **Everywhere else** (planner, notebook, progress, settings, admin, auth): tokens and type only.

## Reference

The chosen mockup (direction A) was shown in the conversation: warm paper, a Fraunces lesson title, a family label with
a dot, the trace on the soft surface with the active cell filled in the family colour, serif prose, and a chapter
outline in a ruled right margin. Treat it as the look, not a pixel spec.

## Left to the builder

- Exact spacing values per component.
- Which of the experiment visual models need colour tweaks after the token swap.
- How the family mark is drawn: a filled dot is fine; a glyph per family is optional.

## Verification

- Frontend type check and unit tests.
- The production build.
- The browser suite, including the catalogue sweep at desktop and phone widths, dark mode and reduced motion.
- Before and after screenshots of the five key screens in both themes.
