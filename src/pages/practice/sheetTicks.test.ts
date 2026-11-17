import { describe, expect, it } from "vitest";
import { lessonForPattern, toggle } from "./sheetTicks";

describe("sheet ticks", () => {
  it("adds once, removes cleanly and keeps order", () => {
    expect(toggle(["a"], "b", true)).toEqual(["a", "b"]);
    expect(toggle(["a", "b"], "b", true)).toEqual(["a", "b"]);
    expect(toggle(["a", "b"], "a", false)).toEqual(["b"]);
    expect(toggle([], "x", false)).toEqual([]);
  });

  it("points a pattern at the 1on1 lesson that teaches it, or at nothing", () => {
    expect(lessonForPattern("Two Pointers")).toBe("lesson-two-pointers");
    expect(lessonForPattern("Arrays & Hashing")).toBe("lesson-hashing");
    expect(lessonForPattern("Bit Manipulation")).toBeNull();
  });
});
