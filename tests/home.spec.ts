import { test, expect } from "@playwright/test";

test("home shows the next step, activity, what is happening and what was asked recently", async ({ page }) => {
  await page.goto("/home");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  const next = page.locator(".dash-next");
  await expect(next).toBeVisible();
  await expect(next.getByRole("link").first()).toHaveAttribute("href", /\/learn\//);
  await expect(page.locator(".dash-activity")).toContainText(/streak/i);
  await expect(page.locator(".dash-heat [data-date]")).toHaveCount(84);
  await expect(page.locator(".dash-happening li").first()).toBeVisible();
  await expect(page.locator(".dash-asked")).toContainText(/Recently asked/);
  await expect(page.locator(".dash-links a")).toHaveCount(6);
});

test("recently asked lists learner reports, or says there are none yet", async ({ page }) => {
  await page.route("**/api/v1/reports/recent", (r) =>
    r.fulfill({ json: [{ questionId: "lc-two-sum", title: "Two Sum", url: "https://leetcode.com/problems/two-sum/", source: "LeetCode", company: "Flipkart", stage: "Interview", month: "2026-11", reports: 3 }] }),
  );
  await page.goto("/home");
  const asked = page.locator(".dash-asked");
  await expect(asked).toContainText("Two Sum");
  await expect(asked).toContainText("Flipkart");
  await expect(asked.getByRole("link", { name: /Two Sum/ })).toHaveAttribute("href", "/practice/q/lc-two-sum");
  await page.unroute("**/api/v1/reports/recent");
  await page.route("**/api/v1/reports/recent", (r) => r.fulfill({ json: [] }));
  await page.reload();
  await expect(page.locator(".dash-asked")).toContainText(/No reports yet/);
});

test("home fits a phone and survives a failing contests source", async ({ page }) => {
  await page.route("**/api/v1/contests", (r) => r.fulfill({ status: 503, json: { message: "down" } }));
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/home");
  await expect(page.locator(".dash-next")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
