import { test, expect } from "@playwright/test";

const soon = (hours: number) => new Date(Date.now() + hours * 3_600_000).toISOString().replace(/\.\d{3}Z$/, "Z");
const DATA = {
  contests: [
    { id: "atcoder-abc485", platform: "AtCoder", title: "AtCoder Beginner Contest 485", start: soon(5), durationMinutes: 100, url: "https://atcoder.jp/contests/abc485" },
    { id: "codeforces-2288", platform: "Codeforces", title: "Codeforces Round (Div. 2)", start: soon(30), durationMinutes: 120, url: "https://codeforces.com/contests/2288" },
    { id: "codeforces-2290", platform: "Codeforces", title: "Educational Round", start: soon(80), durationMinutes: 120, url: "https://codeforces.com/contests/2290" },
  ],
  sources: [
    { platform: "Codeforces", ok: true, fetchedAt: soon(-0.2) },
    { platform: "AtCoder", ok: false, fetchedAt: soon(-2) },
  ],
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/contests", (route) => route.fulfill({ json: DATA }));
});

test("contests are listed by day with a countdown, filterable by platform", async ({ page }) => {
  await page.goto("/contests");
  await expect(page.locator(".contest-row")).toHaveCount(3);
  await expect(page.locator(".contest-row").first()).toContainText("AtCoder Beginner Contest 485");
  await expect(page.locator(".contest-row").first()).toContainText(/in \d+ h/);
  await expect(page.locator(".contest-day").first()).toBeVisible();
  await page.getByRole("button", { name: "Codeforces", exact: true }).click();
  await expect(page.locator(".contest-row")).toHaveCount(2);
  await page.getByRole("button", { name: "All", exact: true }).click();
  await expect(page.locator(".contest-row")).toHaveCount(3);
});

test("a contest can be added to a calendar as an .ics file", async ({ page }) => {
  await page.goto("/contests");
  const download = page.waitForEvent("download");
  await page.locator(".contest-row").first().getByRole("button", { name: /Add .* to calendar/ }).click();
  expect((await download).suggestedFilename()).toBe("atcoder-abc485.ics");
});

test("an unreachable source is named, and LeetCode and CodeChef are linked", async ({ page }) => {
  await page.goto("/contests");
  await expect(page.getByRole("status")).toContainText("AtCoder");
  await expect(page.getByRole("link", { name: /LeetCode contests/ })).toHaveAttribute("href", "https://leetcode.com/contest/");
  await expect(page.getByRole("link", { name: /CodeChef contests/ })).toHaveAttribute("href", "https://www.codechef.com/contests");
});

test("the sidebar links to contests and the page fits a phone", async ({ page }) => {
  await page.goto("/home");
  await expect(page.getByRole("navigation", { name: "Main navigation" }).getByRole("link", { name: "Contests" })).toHaveAttribute("href", "/contests");
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/contests");
  await expect(page.locator(".contest-row").first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});

test("when both sources are down the banner says so plainly, with the time of the last check, and ended contests are hidden", async ({ page }) => {
  await page.unroute("**/api/v1/contests");
  await page.route("**/api/v1/contests", (route) =>
    route.fulfill({
      json: {
        contests: [
          { id: "codeforces-1", platform: "Codeforces", title: "Already over", start: soon(-5), durationMinutes: 60, url: "https://codeforces.com/contests/1" },
          { id: "codeforces-2", platform: "Codeforces", title: "Still to come", start: soon(10), durationMinutes: 60, url: "https://codeforces.com/contests/2" },
        ],
        sources: [
          { platform: "Codeforces", ok: false, fetchedAt: soon(-3) },
          { platform: "AtCoder", ok: false, fetchedAt: soon(-3) },
        ],
      },
    }),
  );
  await page.goto("/contests");
  const banner = page.getByRole("status");
  await expect(banner).toContainText("Codeforces and AtCoder couldn't be reached");
  await expect(banner).toContainText("last checked");
  await expect(banner).not.toContainText("The others are current");
  await expect(page.locator(".contest-row")).toHaveCount(1);
  await expect(page.locator(".contest-row")).toContainText("Still to come");
});
