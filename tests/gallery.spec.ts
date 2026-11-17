import { test, expect } from "@playwright/test";

test("the library links to every animation in one place, loaded only when asked", async ({ page }) => {
  const traces: string[] = [];
  page.on("request", (r) => r.url().includes("/api/v1/experiments") && traces.push(r.url()));
  await page.goto("/learn");
  await page.getByRole("link", { name: /All animations/ }).click();
  await expect(page).toHaveURL(/\/learn\/animations$/);
  await expect(page.locator(".animation-card")).toHaveCount(33);
  expect(traces.length).toBe(0);
  const first = page.locator(".animation-card").first();
  await first.getByRole("button", { name: /Play this animation/ }).click();
  await expect(first.locator(".experiment, [class*='experiment']").first()).toBeVisible();
  expect(traces.length).toBeGreaterThan(0);
  await expect(first.getByRole("link", { name: /Open the lesson/ })).toHaveAttribute("href", /\/learn\/lesson-/);
});

test("the animations page fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/learn/animations");
  await expect(page.locator("h1")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
