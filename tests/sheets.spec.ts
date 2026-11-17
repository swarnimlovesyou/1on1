import { test, expect } from "@playwright/test";

test("a guest works through Blind 75: ticks persist, rows open here or on LeetCode and point to a lesson", async ({ page }) => {
  await page.goto("/practice?tab=sheets");
  await expect(page.locator(".sheet-card")).toHaveCount(2);
  await expect(page.getByText(/MIT/).first()).toBeVisible();
  await page.getByRole("link", { name: /Blind 75/ }).click();
  await expect(page.locator(".sheet-row")).toHaveCount(75);
  const first = page.locator(".sheet-row").first();
  await expect(first.getByRole("link", { name: /Solve here/ })).toHaveAttribute("href", /\/practice\/q\/lc-/);
  await expect(first.locator("a[href^='https://leetcode.com/problems/']")).toHaveCount(1);
  await expect(first.getByRole("link", { name: /Learn/ })).toHaveAttribute("href", "/learn/lesson-hashing");
  await first.getByRole("checkbox").check();
  await expect(page.locator(".sheet-progress")).toContainText("1 of 75");
  await page.reload();
  await expect(page.locator(".sheet-row").first().getByRole("checkbox")).toBeChecked();
});

test("sheets explain why Striver's lists are linked rather than copied", async ({ page }) => {
  await page.goto("/practice?tab=sheets");
  await expect(page.getByRole("link", { name: /takeuforward/ })).toHaveAttribute("href", /^https:\/\/takeuforward\.org/);
});

test("a sheet fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/practice?tab=sheets&sheet=neetcode-150");
  await expect(page.locator(".sheet-row").first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});

test("a damaged saved tick list does not break the sheet, and row actions name their question", async ({ page }) => {
  await page.goto("/practice?tab=sheets");
  await page.evaluate(() => localStorage.setItem("1on1-sheet-ticks", "{}"));
  await page.goto("/practice?tab=sheets&sheet=blind-75");
  await expect(page.locator(".sheet-row")).toHaveCount(75);
  await expect(page.getByRole("link", { name: /Solve here\s*:\s*Two Sum$/ })).toHaveCount(1);
});
