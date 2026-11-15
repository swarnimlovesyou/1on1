---
name: 1on1
description: "An interactive study notebook for understanding algorithms through reading, experiments, and practice."
colors:
  bg: "#f7f8fa"
  surface: "#fff"
  surface-soft: "#f1f3f8"
  ink: "#202735"
  muted: "#667085"
  line: "#e5e8ef"
  accent: "#3459e6"
  accent-wash: "#edf1ff"
  success: "#17825d"
  warning: "#966315"
  error: "#c44040"
  dark-bg: "#11151d"
  dark-surface: "#191f2a"
  dark-surface-soft: "#212938"
  dark-ink: "#edf1f8"
  dark-muted: "#a5afc0"
  dark-line: "#30394a"
  dark-accent: "#91a7ff"
  dark-accent-wash: "#242f53"
  dark-success: "#6ad5ab"
  dark-warning: "#eac776"
  dark-error: "#ff9797"
typography:
  display:
    fontFamily: '"Geist", sans-serif'
    fontSize: "43px"
    fontWeight: 600
    lineHeight: 1.18
    letterSpacing: "-0.04em"
  headline:
    fontFamily: '"Geist", sans-serif'
    fontSize: "36px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  title:
    fontFamily: '"Geist", sans-serif'
    fontSize: "22px"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "-0.025em"
  body:
    fontFamily: '"Geist", sans-serif'
    fontSize: "14px"
    fontWeight: 400
  notebook-prose:
    fontFamily: '"Geist", sans-serif'
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.9
  label:
    fontFamily: '"Geist", sans-serif'
    fontSize: "13px"
    fontWeight: 500
  control:
    fontFamily: '"Geist", sans-serif'
    fontSize: "13px"
    fontWeight: 500
  control-small:
    fontFamily: '"Geist", sans-serif'
    fontSize: "12px"
    fontWeight: 500
  code:
    fontFamily: '"JetBrains Mono", monospace'
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.75
rounded:
  "4": "4px"
  "5": "5px"
  "7": "7px"
  "8": "8px"
  "9": "9px"
  "10": "10px"
  "12": "12px"
  circle: "50%"
spacing:
  "4": "4px"
  "8": "8px"
  "12": "12px"
  "16": "16px"
  "20": "20px"
  "24": "24px"
  "25": "25px"
  "32": "32px"
  "36": "36px"
  "40": "40px"
  "64": "64px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    typography: "{typography.control}"
    rounded: "{rounded.8}"
    padding: "12px 18px"
  button-primary-dark:
    backgroundColor: "{colors.dark-accent}"
    textColor: "{colors.dark-bg}"
    typography: "{typography.control}"
    rounded: "{rounded.8}"
    padding: "12px 18px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.8}"
    padding: "12px 18px"
  button-secondary-hover:
    backgroundColor: "{colors.surface-soft}"
  button-small:
    typography: "{typography.control-small}"
    rounded: "{rounded.8}"
    padding: "9px 13px"
  button-icon:
    textColor: "{colors.muted}"
    rounded: "{rounded.7}"
    height: "36px"
    width: "36px"
  button-icon-hover:
    backgroundColor: "{colors.accent-wash}"
    textColor: "{colors.accent}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.8}"
    padding: "11px 13px"
  navigation-item:
    textColor: "{colors.muted}"
    rounded: "{rounded.7}"
    padding: "10px 13px"
  navigation-item-hover:
    backgroundColor: "{colors.surface-soft}"
    textColor: "{colors.ink}"
  navigation-item-active:
    backgroundColor: "{colors.accent-wash}"
    textColor: "{colors.accent}"
  chip:
    backgroundColor: "{colors.surface-soft}"
    textColor: "{colors.ink}"
    rounded: "{rounded.5}"
    padding: "5px 9px"
  topic-filter:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
    rounded: "{rounded.5}"
    padding: "7px 11px"
  topic-filter-active:
    backgroundColor: "{colors.accent-wash}"
    textColor: "{colors.accent}"
  learning-path:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.12}"
    padding: "26px"
  experiment:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.12}"
  experiment-compact:
    rounded: "{rounded.9}"
---

# Design System: 1on1

## Overview

**Creative North Star: "Blue-ink study notebook"**

1on1 is an interactive study notebook: chapter text, working diagrams, marginal context, and saved annotations share a calm, precise, welcoming interface. Neutral surfaces carry the reading and working space; cobalt identifies actions, selection, and the current computational state.

The approved direction is implemented through code, using Geist Sans and JetBrains Mono with light, dark, and system theme choices. The acknowledged direction seed (`ac92d60e`) remains provenance for the approved notebook direction. The measurements below capture the finished source rather than the provisional seed measurements.

**Key Characteristics:**

- Calm neutral surfaces with a cobalt accent.
- Readable chapter text beside working algorithm diagrams.
- Whitespace, fine separators, and functional frames organize the workspace.
- Shared theme roles, visible focus, and responsive study layouts.

## Colors

The palette pairs neutral reading surfaces with a single cobalt accent. Frontmatter is the normative color record; each `dark-` entry is the matching role under `data-theme="dark"`.

### Primary

- **Cobalt accent:** primary actions, links, selected navigation, active array cells, and current code lines.
- **Cobalt wash:** selected backgrounds, contextual help, and text selection. The wash supports the accent rather than becoming a second accent.

### Neutral

- **Canvas:** the page and topbar background.
- **Surface:** navigation, fields, experiment frames, and bounded working containers.
- **Soft surface:** explanations, chips, and hover backgrounds.
- **Ink:** primary reading text.
- **Muted ink:** supporting copy, metadata, and inactive controls.
- **Line:** fine dividers, field strokes, and structural borders.

### Feedback

Success, warning, and error roles each have light and dark values. Their application includes explanatory text or an icon: completed concepts, inline warnings, retryable errors, and experiment status.

## Typography

**Display and Body Font:** Geist Sans, declared in CSS as `"Geist", sans-serif`.

**Label/Mono Font:** JetBrains Mono with a monospace fallback, used for code, indices, variables, complexity, and step counts.

**Character:** Geist supplies a clear reading hierarchy; JetBrains Mono makes execution data distinguishable from explanatory prose. Headings use restrained negative tracking, while supporting text stays compact.

### Hierarchy

- **Display:** Home's main heading uses the frontmatter display role. It becomes (49px) on wide screens and (36px) on mobile; intermediate viewport rules also adjust it.
- **Headline:** the default page heading uses the headline role. Notebook titles use a separate observed treatment (43px, 1.16 line height, -0.04em tracking, 19ch maximum width), reducing to (37px) and then (35px).
- **Title:** section headings use the title role; smaller section headings commonly use (19px). Subheadings use (16px).
- **Body:** the root text size uses the body role. Paragraphs default to (1.7) line height; notebook prose uses its own role and a maximum reading measure (68ch), reducing to (14px) on mobile.
- **Label and controls:** labels and standard buttons use the frontmatter roles. Navigation and metadata commonly use (9–12px), with case and tracking applied only where present in the source.
- **Code:** preformatted blocks use the code role. Experiment variables, indices, and step counts use smaller mono treatments suited to their local layout.

## Layout

The desktop workspace is a two-column shell with left navigation (232px) and a flexible main canvas. The sticky topbar is (74px) high. Main content has padding (38px 42px 0), a maximum width (1500px), and automatic horizontal margins. Repeated spacing values are captured in frontmatter; the source also uses component-specific measurements.

The notebook centers a chapter margin (165px) and a reading column up to (760px), separated by (40px). Its chapter navigation is sticky below the topbar. Text, separators, and whitespace provide the reading structure. Home's featured lesson is an unframed composition of lesson copy and a framed experiment; the outer feature has no border, surface fill, or corner treatment.

Responsive rules follow the implemented media queries:

- At or below (1200px), navigation narrows to (205px), page padding becomes (30px 28px 0), and the notebook margin narrows.
- At or below (1023px), navigation narrows to (180px), the featured lesson and lower Home sections stack, and notebook chapter navigation becomes a wrapping row above the content.
- At or below (767px), the sidebar becomes a modal drawer (275px), the topbar becomes (62px), global search is hidden, and page padding becomes (25px 20px 0). Working layouts stack; experiment input controls wrap.
- At or above (1600px), page side padding and featured-lesson spacing increase to (65px).

Diagram and array viewports retain internal scrolling when needed. Wrapping and local overflow keep the surrounding page usable.

## Elevation & Depth

The workspace is predominantly flat. Surface tones, one-pixel borders, and separators establish structure. Resting experiment and learning-path frames have no shadow. Shadows are reserved for the toast, contextual drawer, expanded experiment scrim, and field focus treatment; their exact source values are recorded in the sidecar.

The toast uses the theme-aware shadow custom property. The tutor drawer uses a leftward shadow. The expanded experiment uses a viewport-sized shadow as its scrim. Focused fields use an accent-wash ring, while keyboard focus on buttons and links uses a visible outline (3px) with an offset (4px).

## Shapes

Small badges use the smallest corners; chips and filters use compact corners; inputs and standard buttons use the control radius. Navigation, icon controls, array cells, and explanation blocks use the compact control radius. Experiments and learning-path containers use the panel radius, with a smaller radius on compact experiments. Dots, avatars, and round concept-open controls use circular geometry.

Borders are thin and neutral at rest. Selected filters, checkpoint answers, and active computational elements shift their border and text to the accent. Clipping belongs to working frames that contain visualizations, rather than to every text section.

## Components

### Buttons

Standard actions have gently curved corners, a minimum height (44px), and a text/icon gap (10px). Primary actions use accent fill; their dark-theme foreground is the dark canvas role. Secondary actions use a surface fill and a neutral border. Small buttons reduce padding and use a minimum height (38px) with text (12px).

Buttons move upward (1px) on hover with background and transform transitions (0.18s). Primary hover applies brightness (0.96); secondary hover uses the soft surface. Disabled buttons lower opacity (0.5). Icon controls have muted ink, becoming accent on an accent-wash background when hovered; selected bookmarks retain accent ink.

### Inputs / Fields

Fields use the surface, ink, neutral stroke, and control radius from frontmatter. Focus changes the stroke to accent and adds the wash ring described above. Placeholders use muted ink at opacity (0.85). Textareas use line height (1.6), vertical resizing, and an accent caret. Search wrappers remove the inner input border and keep their own compact frame.

### Navigation

Desktop navigation uses stacked text/icon rows with a minimum height (43px), gaps (12px), text (12px, weight 500), and the frontmatter item padding. Hover adds a soft surface; the current route uses accent text and wash. Mobile navigation reuses these roles inside the drawer, with larger row padding (12px) and text (13px). Chapter links remain quiet marginal text and turn accent on hover.

### Chips

Informational chips use soft surface, compact corners, and text (12px). Topic filters are separate interactive buttons: neutral stroke at rest, accent stroke/text/wash when active. Status and difficulty labels retain their semantic text or icon context.

### Cards / Containers

Learning paths and checkpoints are bounded reading or task containers with neutral borders and panel corners. Learning paths use padding (26px); checkpoints use padding (25px). Resting containers remain flat. Lesson lists use separator rows. Home's featured lesson stays unframed around its copy and experiment.

### Interactive experiment

The experiment is the functional frame for an algorithm trace. Its header, visualization, variables, explanation, playback, editable input, and optional textual transcript form a single working unit. The header is (44px), visualization has a minimum height (180px), and the standard array cell is (47px by 51px). Active values use accent text, border, and wash. Mono indices, a numbered explanation, and a step counter make state legible beyond color.

Compact experiments reduce the frame radius, header, cells, and control sizes. Expanded experiments become a fixed working surface with a scrim. Playback is explicitly started, paused, reset, or stepped by the learner, with selectable intervals (1500ms, 900ms, 450ms). Array state transitions use (0.2s); lesson-link color uses (0.15s). The reduced-motion media query removes CSS animation and transitions. Loading skeletons use the source pulse animation; errors show a recovery action.

## Do's and Don'ts

### Do:

- **Do** use the corresponding light or dark semantic roles together.
- **Do** keep chapter prose readable at its observed measure and line height.
- **Do** show current experiment state with values, indices, explanation, and playback context.
- **Do** retain the visible focus treatments and reduced-motion override.
- **Do** preserve Home's unframed featured lesson and the experiment's functional frame.

### Don't:

- **Don't** apply the provisional seed measurements when the frontmatter or implemented layout supplies a different value.
- **Don't** turn separator-based lesson rows into a grid of framed cards.
- **Don't** use status color as the only explanation of a result.
- **Don't** treat synthesized palette ramps or additional accent colors as implemented tokens.
