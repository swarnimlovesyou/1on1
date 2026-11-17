import { expect, it } from "vitest";
import { guidePassed, trackProgress } from "./progress";

it("passes a guide only when every question has a correct attempt, whatever came before", () => {
  const attempts = [
    { challengeId: "a", correct: false },
    { challengeId: "a", correct: true },
  ];
  expect(guidePassed(["a", "b"], attempts)).toBe(false);
  expect(guidePassed(["a", "b"], [...attempts, { challengeId: "b", correct: true }])).toBe(true);
  expect(guidePassed([], attempts)).toBe(false);
});

it("counts passed guides per track", () => {
  const guides = [
    { track: "cs-fundamentals", challengeIds: ["a"] },
    { track: "cs-fundamentals", challengeIds: ["b"] },
    { track: "aptitude", challengeIds: ["c"] },
  ];
  expect(trackProgress(guides, [{ challengeId: "a", correct: true }])).toEqual({
    "cs-fundamentals": { passed: 1, total: 2 },
    aptitude: { passed: 0, total: 1 },
  });
});
