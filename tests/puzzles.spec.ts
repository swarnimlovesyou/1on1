import { test, expect } from "@playwright/test";

test("the puzzles track lists 20 puzzles", async ({ page }) => {
  await page.goto("/prep/puzzles");
  await expect(page.locator(".prep-guides li")).toHaveCount(20);
});

test("a puzzle reveals hints in order, then the solution, and checks a typed answer on the server", async ({ page }) => {
  await page.goto("/prep/puzzles");
  await page.locator(".prep-guides li a").first().click();
  await expect(page.locator(".puzzle-statement")).toBeVisible();
  await expect(page.locator(".puzzle-hints li")).toHaveCount(0);
  await page.getByRole("button", { name: "Show a hint" }).click();
  await expect(page.locator(".puzzle-hints li")).toHaveCount(1);
  await page.getByRole("button", { name: "Show the next hint" }).click();
  await expect(page.locator(".puzzle-hints li")).toHaveCount(2);
  await expect(page.getByRole("button", { name: /next hint/ })).toHaveCount(0);
  await expect(page.locator(".puzzle-solution")).toHaveCount(0);
  await page.getByRole("button", { name: "Show the solution" }).click();
  await expect(page.locator(".puzzle-solution li").first()).toBeVisible();
  const box = page.getByRole("textbox", { name: "Your answer" });
  if (await box.count()) {
    await box.fill("definitely not the answer");
    await page.getByRole("button", { name: "Check" }).click();
    await expect(page.getByRole("status")).toContainText("Not quite");
  }
});

test("a puzzle page fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/prep/puzzles");
  await page.locator(".prep-guides li a").last().click();
  await expect(page.locator(".puzzle-statement")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
