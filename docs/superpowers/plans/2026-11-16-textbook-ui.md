# Textbook UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle 1on1 as a calm, well-printed textbook. The design system changes on every page, and the landing page,
home, library and concept map, lessons and problems get a deeper treatment.

**Architecture:** One family module maps lessons and problems to six algorithm families. New tokens and fonts in
`src/styles.css` move every page at once. Then the five key screens are restyled and given a `--family` colour on their
root. No data, API or route changes.

**Tech Stack:**
- React 19, Vite, TypeScript and Vitest.
- Fonts from `@fontsource` packages.
- The Monaco editor, through `@monaco-editor/react`.
- Playwright for the browser suite.

**Spec:** `docs/superpowers/specs/2026-11-16-textbook-ui-design.md`

## Global Constraints

- **Fonts are bundled through `@fontsource`; no runtime CDN:**
  - display: Fraunces (400/500)
  - prose: Source Serif 4 (400)
  - interface: Inter Tight (400/500)
  - code: JetBrains Mono (kept)
- **Type scale (px):** 12 / 13 / 15 / 17 / 22 / 30 / 40. Prose is 17 px with line-height 1.75, at most about 65
  characters per line.
- **Paper (light):** page `#FBFAF7`, surface `#FFFFFF`, soft `#F1EEE6`, ink `#1F2430`, muted `#5E6370`, rule `#E7E3DA`.
- **Night (dark):** page `#17181B`, surface `#1E2024`, soft `#25282D`, ink `#ECE8DF`, muted `#A39F96`, rule `#33363C`.
- **Interface accent (focus, selection, active, progress):** `#2F4A6E` on paper, `#A9BEDC` at night. Primary buttons and
  links are ink.
- **Families (light / night):**
  - foundations `#3F5873` / `#9DB4CC`
  - searching `#2E6B5E` / `#7CC2B0`
  - linear `#8A5A12` / `#E0B465`
  - recursion `#6B3F73` / `#C79BD0`
  - trees `#94431F` / `#E59A74`
  - graphs `#2F55A4` / `#8EAEF0`
- **State colours keep their meaning:** success means accepted, warning means review due, error means failed.
- **Radius:** 10 px for cards, 6 px for controls. Hairline rules instead of shadows; one soft shadow only on popovers
  and the tutor drawer.
- **The theme switch stays:** `data-theme` light or dark, and system. Body text meets WCAG AA in both themes. Focus is
  visible and reduced motion is respected. No horizontal scroll at 390 px.
- **No changes to features, routes, APIs, data or copy,** beyond small label tweaks a layout needs.

## Review Focus

1. **Night-theme contrast:** muted text and family colours on night surfaces must stay readable (AA at 4.5:1 for text).
   This is pinned by the contrast test in Task 2.
2. **Phone width:** Fraunces is wider than Geist, so long titles such as "Dynamic Programming: Memoization and
   Tabulation" must wrap without sideways scroll at 390 px. Pinned by the catalogue sweep in Task 6.
3. **Unknown or new topics:** a problem whose topics match no family must still render, as Foundations. Pinned by a test
   in Task 1.
4. **The code editor following the theme:** switching light, dark or system must switch the Monaco theme. Pinned by a
   test in Task 3.
5. **Progress still visible on the concept map:** explored, passed, accepted and review-due styles must stay distinct
   after the token swap. Pinned by a check in Task 4.

---

### Task 1: Algorithm families

**Files:**
- Create: `src/families.ts`
- Create: `src/components/FamilyMark.tsx`
- Test: `src/families.test.ts`

**Interfaces:**
- Produces:
  - `type FamilyId = "foundations" | "searching" | "linear" | "recursion" | "trees" | "graphs"`
  - `FAMILIES: Record<FamilyId, { label: string }>`, with these labels:

    | Id | Label |
    | --- | --- |
    | `foundations` | Foundations |
    | `searching` | Searching and sorting |
    | `linear` | Linear structures |
    | `recursion` | Recursion and DP |
    | `trees` | Trees and heaps |
    | `graphs` | Graphs |

  - `familyOfLesson(lesson: { id: string; conceptId?: string }): FamilyId`
  - `familyOfProblem(topics: string[]): FamilyId`
  - `familyVar(id: FamilyId): string`, which returns `"var(--family-<id>)"`
  - `<FamilyMark family={FamilyId} label?: boolean />`, which renders a dot in the family colour and, when `label` is
    set, the family label. The dot is `aria-hidden`; the label is text.

- [ ] **Step 1: Write the failing tests** in `src/families.test.ts`:
  - `familyOfLesson` maps every concept to its family:

    | Family | Concepts |
    | --- | --- |
    | foundations | complexity, arrays, strings, hashing |
    | searching | sorting, prefix-sums, two-pointers, fixed-window, variable-window, binary-search, intervals |
    | linear | matrices, linked-lists, stacks, queues |
    | recursion | recursion, backtracking, dynamic-programming |
    | trees | binary-trees, bst, heaps |
    | graphs | graphs, bfs, dfs |

  - Lessons without a concept map like this:

    | Lesson | Family |
    | --- | --- |
    | lesson-avl | trees |
    | lesson-trie | trees |
    | lesson-dijkstra | graphs |
    | lesson-max-flow | graphs |
    | lesson-quickselect | searching |
    | lesson-bloom-filter | foundations |
    | lesson-set-cover | foundations |

  - `familyOfProblem` uses the first topic that maps:
    - `["Arrays","Two pointers"]` gives `foundations`;
    - `["Two pointers","Arrays"]` gives `searching`;
    - `["Stacks & queues"]` gives `linear`;
    - `["Dynamic programming"]` gives `recursion`;
    - `["Heaps"]` gives `trees`;
    - `["Graphs"]` gives `graphs`.
  - Topic mapping:
    - Strings, Hashing, Probabilistic structures and Greedy algorithms are `foundations`.
    - Sorting, Search, Sliding window, Two pointers and Randomization are `searching`.
    - Recursion is `recursion`.
    - Trees and Text search are `trees`.
  - Unknown topics fall back: `["Quantum"]` and `[]` give `foundations`.
  - `familyVar("graphs")` returns `"var(--family-graphs)"`.

- [ ] **Step 2: Run** `npx vitest run src/families.test.ts`. Expected: FAIL (module not found).

- [ ] **Step 3: Implement `src/families.ts` and `FamilyMark.tsx`** with the signatures above. Use plain lookup tables
  keyed by concept id, lesson id and topic. `FamilyMark` uses class `family-mark`, styled in Task 2.

- [ ] **Step 4: Run** `npx vitest run src/families.test.ts`. Expected: PASS.

- [ ] **Step 5: Commit** `src/families.ts src/components/FamilyMark.tsx src/families.test.ts` with the message "Map
  lessons and problems to six algorithm families".

### Task 2: Tokens, fonts and type

**Files:**
- Modify: `package.json`, `package-lock.json` (add `@fontsource/fraunces`, `@fontsource/source-serif-4`,
  `@fontsource/inter-tight`; remove `@fontsource/geist`)
- Modify: `src/main.tsx` (font imports)
- Modify: `src/styles.css` (`:root` and `:root[data-theme="dark"]` tokens; base type; replace the 34 raw hex values
  with tokens; make the path markers `.path-0`, `.path-1` and `.path-2` neutral; style `.family-mark`)
- Test: `src/theme.test.ts`

**Interfaces:**
- Produces the CSS custom properties every later task uses:
  - Kept names, new values: `--bg`, `--surface`, `--surface-soft`, `--ink`, `--muted`, `--line`, `--accent` (the
    interface accent), `--accent-wash`, `--success`, `--warning`, `--error`.
  - New colour: `--family-<id>` and `--family-<id>-wash` for each of the six families.
  - New type: `--font-display`, `--font-text`, `--font-sans`, `--font-mono`.
  - New shape: `--radius-card: 10px`, `--radius-control: 6px`.
- Produces the utility classes `.display` (Fraunces) and `.prose` (Source Serif 4, 17 px / 1.75, `max-width: 65ch`).
- **Keeping the existing token names is the key decision.** Most of the 619 `var(--…)` uses then restyle with no edits.

- [ ] **Step 1: Write the failing test** in `src/theme.test.ts`.
  - Read `src/styles.css` as text and parse the `--*` values from the light `:root` block and the dark block.
  - Assert that the contrast ratio is at least 4.5 for each pair below, in each theme:
    - `--ink` on `--bg`
    - `--muted` on `--bg`
    - `--muted` on `--surface`
    - `--accent` on `--bg`
    - each `--family-<id>` on `--bg` and on `--surface-soft`
  - Assert that `--bg` is `#FBFAF7` in the light block and `#17181B` in the dark block.

- [ ] **Step 2: Run** `npx vitest run src/theme.test.ts`. Expected: FAIL, because today's `--bg` is `#f7f8fa`.

- [ ] **Step 3: Install the fonts** with `npm install @fontsource/fraunces @fontsource/source-serif-4 @fontsource/inter-tight`
  and `npm uninstall @fontsource/geist`. In `main.tsx`, import the latin 400/500 weights of Fraunces and Inter Tight,
  latin 400 of Source Serif 4, and keep JetBrains Mono.

- [ ] **Step 4: Rewrite the tokens and base type** in `src/styles.css` with the Global Constraints values.
  - Headings use `--font-display`; the body uses `--font-sans`.
  - Swap the remaining raw hex values for tokens.
  - Change `box-shadow` to none, except on `.tutor-drawer` and popovers.
  - Change radii to the two tokens.

- [ ] **Step 5: Run the checks.**
  - `npx vitest run`: all pass.
  - `npx tsc --noEmit -p .`: no output.
  - `npm run build`: builds.

- [ ] **Step 6: Commit** with the message "Switch to paper and night palettes and textbook type".

### Task 3: Editor themes

**Files:**
- Create: `src/components/editorTheme.ts`
- Modify: `src/components/CodeEditor.tsx:20-45`
- Test: `src/components/editorTheme.test.ts`

**Interfaces:**
- Produces `editorTheme(theme: "light" | "dark" | "system", prefersDark: boolean): "1on1-paper" | "1on1-night"`,
  in `editorTheme.ts`, kept apart from the Monaco import so it can be unit tested. `CodeEditor.tsx` defines both Monaco
  themes, with backgrounds and foregrounds from the paper and
  night palettes and the interface accent for the cursor and selection.

- [ ] **Step 1: Write the failing test.** `editorTheme` gives these results:
  - `("light", true)` → `"1on1-paper"`
  - `("dark", false)` → `"1on1-night"`
  - `("system", true)` → `"1on1-night"`
  - `("system", false)` → `"1on1-paper"`

- [ ] **Step 2: Run** `npx vitest run src/components/editorTheme.test.ts`. Expected: FAIL.

- [ ] **Step 3: Implement.** Replace `vs-dark` and `1on1-light` with the two `defineTheme` calls, and pick between them
  with `editorTheme`.

- [ ] **Step 4: Run the test again.** Expected: PASS.

- [ ] **Step 5: Commit** with the message "Give the code editor paper and night themes".

### Task 4: Library, concept map and home

**Files:**
- Modify: `src/pages/Learning.tsx` (`Library` rows, `Home`)
- Modify: `src/pages/LearningMap.tsx` (`ConceptMap` nodes and list, `NextActionCard`, `ReviewsDue`)
- Modify: `src/styles.css` (the matching sections)

**Interfaces:**
- Consumes `familyOfLesson`, `FamilyMark` and `FAMILIES` from Task 1, and the tokens from Task 2.
- Library: on the "All concepts" tab, rows are grouped under a family heading, in `FAMILIES` order, when no topic,
  path or search filter is active. Otherwise the list stays flat. Each row shows a `FamilyMark`.
- Concept map: nodes keep their `state-*` and `due` classes. Each node gains a `FamilyMark` dot. The node border is not
  the family colour.
- Home: the next action and due reviews show a `FamilyMark`, with lessons looked up through `familyOfLesson`.

- [ ] **Step 1: Implement** the above, plus styles for the family grouping heading and the dot.

- [ ] **Step 2: Check in the browser.**
  - `/learn` shows six family groups.
  - On the concept map, nodes in different states still look different in both themes.
  - Run `npx playwright test tests/platform.spec.ts tests/themes.spec.ts`. Expected: pass.

- [ ] **Step 3: Commit** with the message "Group the library by family and mark families on the map and home".

### Task 5: Lesson and problem pages

**Files:**
- Modify: `src/pages/Learning.tsx` (the lesson page: header, `#idea`, `#experiment`, `#code`, `#pattern`, practice)
- Modify: `src/pages/Practice.tsx` (`ProblemPage` header, statement, editorial)
- Modify: `src/styles.css` (the lesson, experiment and problem sections)
- Modify: `src/components/experiment/*` only where an active or highlight colour is hard-wired to `--accent`; it should
  read `var(--family, var(--accent))`.

**Interfaces:**
- Consumes `familyOfLesson`, `familyOfProblem`, `familyVar` and `FamilyMark`.
- The lesson root and the problem root set `style={{ "--family": familyVar(id) }}`.
- **Lesson header:** a `FamilyMark` with its label, then the title in `.display` at 40 px (30 px under 768 px).
- **Prose:** paragraphs in `#idea`, `#pattern`, the blocks and the editorial use `.prose`.
- **Experiment:** framed on `--surface-soft` with `--radius-card`. The active cell and highlight use `--family`.
- **Practice sections:** separated by hairline rules, not boxes.
- **Problem header:** a `FamilyMark` and a `.display` title. The statement and editorial use `.prose`. The Coach and hints
  stay in `--font-sans`.

- [ ] **Step 1: Implement** the above.

- [ ] **Step 2: Check in the browser.**
  - Look at `lesson-binary-search` (searching, green), `lesson-bfs` (graphs, blue) and `problem-trapped-rain`, in both
    themes and at 390 px.
  - Run `npx playwright test tests/reference-journeys.spec.ts tests/visualizations.spec.ts tests/curriculum.spec.ts`.
    Expected: pass.

- [ ] **Step 3: Commit** with the message "Give lessons and problems the textbook layout and family colour".

### Task 6: Landing page and full verification

**Files:**
- Modify: `src/pages/Learning.tsx` (`Landing`)
- Modify: `src/styles.css` (the landing section)
- Modify: `docs/PHASE2_HANDOFF.md` (one line under "What changed")

**Interfaces:**
- Consumes the tokens, `.display`, `FamilyMark` and the `--family` pattern.
- The landing page keeps its structure and copy. The headline uses `.display`. The hero trace sits on `--surface-soft`
  with `--family: var(--family-searching)`. The story steps and counts are restyled with tokens only.

- [ ] **Step 1: Implement** the landing changes.

- [ ] **Step 2: Run the full checks.**
  - `npm run verify` passes.
  - `npx playwright test` passes all specs, including `tests/catalogue.spec.ts` at 390 and 1440 px.

- [ ] **Step 3: Take before and after screenshots** of the landing page, home, `/learn`, `lesson-binary-search` and
  `problem-trapped-rain`, in both themes. Save them to `.impeccable/review/textbook-*.png`, which is ignored by Git, and
  show them to the owner.

- [ ] **Step 4: Commit** with the message "Restyle the landing page and record the textbook redesign".
