import { test, expect } from "@playwright/test";

test("filters are few, combinable and kept in the URL", async ({ page }) => {
  await page.goto("/learn");
  await expect(page.locator(".topic-filters button")).toHaveCount(0);
  await page.getByRole("combobox", { name: "Family" }).selectOption("graphs");
  await expect(page).toHaveURL(/family=graphs/);
  const rows = page.locator(".concept-row");
  expect(await rows.count()).toBeGreaterThan(0);
  for (const text of await rows.locator(".concept-topic").allInnerTexts()) expect(text).toMatch(/Graph|BFS|DFS|Breadth|Depth|Dijkstra|Flow/i);
  await page.getByRole("combobox", { name: "Difficulty" }).selectOption({ index: 1 });
  await expect(page).toHaveURL(/difficulty=/);
  await page.reload();
  await expect(page.getByRole("combobox", { name: "Family" })).toHaveValue("graphs");
  await page.getByRole("combobox", { name: "Status" }).selectOption("saved");
  await expect(page.getByText(/Nothing saved here yet|No concepts match/)).toBeVisible();
});

test("a learning path is a step timeline with progress and a next step", async ({ page }) => {
  await page.goto("/learn?view=paths");
  await page.getByRole("link", { name: /DSA Foundations/ }).click();
  await expect(page).toHaveURL(/path=path-foundations/);
  const steps = page.locator(".path-step");
  await expect(steps).toHaveCount(42);
  await expect(page.locator(".path-progress")).toContainText("0 of 42");
  await expect(steps.first()).toHaveClass(/next/);
  await expect(page.getByRole("link", { name: /Start the path|Continue the path/ })).toHaveAttribute("href", /\/learn\/lesson-/);
});

test("the sidebar counts every lesson", async ({ page }) => {
  await page.goto("/learn");
  await expect(page.getByRole("navigation", { name: "Main navigation" }).locator(".nav-count")).toHaveText("49");
});
