import { test, expect } from "@playwright/test";

const askedAt = (scope: import("@playwright/test").Locator) => scope.locator(".asked-at");

test("the bank shows where each question was reported, linking to that company's list", async ({ page }) => {
  await page.goto("/practice?tab=bank&q=two%20sum&source=LeetCode");
  const row = page.locator(".bank-row").filter({ has: page.getByRole("link", { name: "Two Sum", exact: true }) }).first();
  await expect(askedAt(row)).toContainText("Asked at");
  await expect(askedAt(row).getByRole("link", { name: "Amazon" })).toHaveAttribute("href", /company=Amazon/);
});

test("sheet rows show where each question was reported", async ({ page }) => {
  await page.goto("/practice?tab=sheets&sheet=blind-75");
  const row = page.locator(".sheet-row").filter({ hasText: "Two Sum" }).first();
  await expect(askedAt(row)).toContainText("Amazon");
});

test("the solve-here page names the companies that reported the question", async ({ page }) => {
  await page.goto("/practice/q/lc-two-sum");
  await expect(askedAt(page)).toContainText("Amazon");
  await expect(askedAt(page)).toContainText(/more|Google/);
});
