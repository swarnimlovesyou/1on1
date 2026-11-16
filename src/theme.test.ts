// @ts-expect-error Node types are not installed; Vitest runs this file under Node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/** Reads the paper (light) and night (dark) token blocks straight from the stylesheet. */
const css: string = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
function block(selector: string) {
  const start = css.indexOf(selector + " {");
  const body = css.slice(start, css.indexOf("}", start));
  return Object.fromEntries([...body.matchAll(/(--[\w-]+):\s*(#[0-9a-fA-F]{6})/g)].map((m) => [m[1], m[2]]));
}
function luminance(hex: string) {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a: string, b: string) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}
const families = ["foundations", "searching", "linear", "recursion", "trees", "graphs"];

describe.each([
  ["paper", ":root", "#FBFAF7"],
  ["night", ':root[data-theme="dark"]', "#17181B"],
])("%s theme", (_, selector, page) => {
  const t = block(selector);
  it("uses the designed page colour", () => {
    expect(t["--bg"]?.toUpperCase()).toBe(page);
  });
  it("keeps text, accent and family colours readable (WCAG AA 4.5:1)", () => {
    const pairs: [string, string][] = [
      ["--ink", "--bg"], ["--muted", "--bg"], ["--muted", "--surface"], ["--accent", "--bg"],
      ...families.flatMap((f): [string, string][] => [[`--family-${f}`, "--bg"], [`--family-${f}`, "--surface-soft"]]),
    ];
    for (const [fg, bg] of pairs) {
      expect(t[fg], fg).toBeDefined();
      expect(contrast(t[fg], t[bg]), `${fg} on ${bg}`).toBeGreaterThanOrEqual(4.5);
    }
  });
});
