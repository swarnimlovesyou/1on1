import { test, expect } from "@playwright/test";

test("the lab measures an algorithm's steps and names the closest growth curve", async ({ page }) => {
  await page.goto("/learn");
  await page.getByRole("navigation", { name: "Main navigation" }).getByRole("link", { name: "Performance lab" }).click();
  await expect(page).toHaveURL(/\/learn\/lab$/);
  await page.getByRole("button", { name: "Merge sort", exact: true }).click();
  await expect(page.locator(".lab-verdict")).toContainText("n log n");
  await expect(page.locator(".lab-point")).toHaveCount(4);
  await expect(page.getByRole("table").locator("tbody tr")).toHaveCount(4);
  await page.getByRole("button", { name: "Binary search", exact: true }).click();
  await expect(page.locator(".lab-verdict")).toContainText("log n");
  await expect(page.getByText(/steps of the real Java trace, not time/)).toBeVisible();
});

test("the lab fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/learn/lab");
  await expect(page.locator(".lab-point").first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
