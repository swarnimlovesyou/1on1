import { test, expect } from "@playwright/test";

const LESSONS: [string, string][] = [
  ["lesson-union-find", ".board-graph"],
  ["lesson-topological-sort", ".board-graph"],
  ["lesson-kruskal", ".board-graph"],
  ["lesson-bellman-ford", ".board-graph"],
  ["lesson-floyd-warshall", ".board-table"],
  ["lesson-segment-tree", ".board-array"],
  ["lesson-fenwick", ".board-array"],
  ["lesson-interval-scheduling", ".board-array"],
  ["lesson-bits", ".board-array"],
  ["lesson-kmp", ".board-array.text"],
  ["lesson-rabin-karp", ".board-array.text"],
  ["lesson-monotonic-stack", ".board-stack, .board-empty"],
  ["lesson-monotonic-queue", ".board-stack, .board-empty"],
  ["lesson-knapsack", ".board-table"],
  ["lesson-lcs", ".board-table"],
  ["lesson-interval-dp", ".board-table"],
];

for (const [id, panel] of LESSONS)
  test(`${id} animates step by step on the trace board`, async ({ page }) => {
    await page.goto("/learn/" + id);
    await expect(page.locator("h1")).toBeVisible();
    const board = page.locator(".board").first();
    await expect(board).toBeVisible();
    await expect(board.locator(panel).first()).toBeVisible();
    const next = page.getByRole("button", { name: "Next step" }).first();
    await expect(next).toBeEnabled();
    const before = await board.innerHTML();
    await next.click();
    await next.click();
    await expect.poll(() => board.innerHTML()).not.toBe(before);
  });

test("a board concept takes custom input", async ({ page }) => {
  await page.goto("/learn/lesson-knapsack");
  await page.getByLabel("Capacity").fill("5");
  await page.getByRole("button", { name: /Update experiment/ }).click();
  await expect(page.locator(".board-table thead th").last()).toHaveText("5");
});

test("the trace board fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/learn/lesson-kruskal");
  await expect(page.locator(".board").first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
