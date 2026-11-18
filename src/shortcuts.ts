import { useEffect } from "react";

/** Single-key shortcuts to the main areas, shown beside the sidebar items and in the key strip. */
export const SHORTCUTS: [key: string, path: string, label: string][] = [
  ["H", "/home", "Home"],
  ["L", "/learn", "Explore concepts"],
  ["A", "/learn/animations", "Animations"],
  ["P", "/practice", "Practice"],
  ["S", "/practice?tab=sheets", "Sheets"],
  ["C", "/contests", "Contests"],
  ["R", "/prep", "Prep"],
  ["N", "/notebook", "My notebook"],
  ["G", "/progress", "Progress"],
];

export const keyFor = (path: string) => SHORTCUTS.find(([, p]) => p === path)?.[0];

/** True while the learner is typing somewhere, so a letter never navigates away from a field or the code editor. */
export function isTyping(target: EventTarget | null) {
  if (!(target instanceof Element)) return false;
  if (target.closest("input, textarea, select, [contenteditable=''], [contenteditable='true'], .monaco-editor, .cm-editor")) return true;
  return !!target.closest("[role='dialog']");
}

export function useShortcuts(go: (path: string) => void, help: () => void) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.ctrlKey || e.metaKey || e.altKey || e.repeat || isTyping(e.target)) return;
      if (e.key === "?") {
        e.preventDefault();
        return help();
      }
      const hit = SHORTCUTS.find(([key]) => key === e.key.toUpperCase() && e.key.length === 1 && !e.shiftKey);
      if (hit) {
        e.preventDefault();
        go(hit[1]);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go, help]);
}
