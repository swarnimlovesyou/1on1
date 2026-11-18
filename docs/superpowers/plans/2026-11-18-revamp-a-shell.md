# Revamp phase A: look, shell and landing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 1on1 takes on the datalis visual system (Geist, mint background, teal accent, light only), a keyboard-first
shell, and a landing page that shows real 1on1 fragments.

**Architecture:** Token values change in `src/styles.css` (names stay, so every page restyles at once); dark tokens and
the theme toggle are removed; a `useShortcuts` hook maps single keys to areas; the landing page is rebuilt from live
components (Experiment, CompanyTags, drill check, contests).

**Tech Stack:** React, Vite, Tailwind v4 tokens, `@fontsource-variable/geist`, Playwright, Vitest.

**Spec:** `docs/superpowers/specs/2026-11-18-revamp-design.md`

## Global Constraints

- Tokens exactly as the spec's table; light only; Geist and Geist Mono everywhere.
- No shortcut fires while typing in an input, textarea, select, contenteditable or code editor.
- Works at 390 px; visible teal focus ring.

## Review Focus

1. **Typing a letter in a search box or the code editor:** never navigates. Pinned in Task 2.
2. **A learner who had dark mode saved in localStorage:** sees the light app, no broken colours. Pinned in Task 1.
3. **Landing fragments when the API is down:** the page still renders its headline and actions. Pinned in Task 3.
4. **Contrast of muted text on the mint background:** at least 4.5:1. Checked in Task 1.
5. **Phone width:** no sideways scroll on landing or shell. Pinned in Tasks 2 and 3.

### Task 1: Tokens, fonts, light only
- `tests/themes.spec.ts` rewritten: no theme toggle; `body` background `rgb(244, 246, 245)`; body font starts with
  "Geist Variable"; a stored `1on1-theme=dark` still renders light. Intermediate widths keep the notebook usable (kept).
- Replace token values; delete the dark token block and `[data-theme="dark"]` rules; remove theme state and toggle.

### Task 2: Keyboard-first shell
- `useShortcuts`: H home, L explore concepts, A animations, P practice, S sheets, C contests, R prep, N notebook,
  G progress; `?` lists them. Sidebar items show their key; a shortcut strip at ≥ 1280 px.
- `tests/shortcuts.spec.ts`: P goes to Practice; typing "p" in the bank search does not; `?` opens the key list.

### Task 3: Landing page
- Hero: headline, two actions, check-marked facts; then live fragments: an animation, a sheet row with "Asked at", a
  drill question being checked, upcoming contests, the key map, learning paths; footer.
- `tests/landing.spec.ts` rewritten for the new structure, API-down rendering and phone width.
