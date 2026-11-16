import { test, expect } from "@playwright/test";

test("the practice list marks every problem with its algorithm family", async ({ page }) => {
  await page.goto("/practice");
  const rows = page.locator(".problem-table tbody tr");
  await expect(rows.first()).toBeVisible({ timeout: 15000 });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);
  await expect(page.locator(".problem-table tbody tr .family-mark")).toHaveCount(count);
});
