import { test, expect } from "@playwright/test";

const LESSON = "/learn/lesson-complexity";

test("the title appears once and the idea opens with a short lead, not a wall of text", async ({ page }) => {
  await page.goto(LESSON);
  await expect(page.getByRole("heading", { level: 1, name: "Time and Space Complexity" })).toBeVisible();
  expect(await page.locator(".notebook-breadcrumb").innerText()).not.toContain("Time and Space Complexity");
  const lead = (await page.locator("#idea .lesson-lead").innerText()).trim();
  expect(lead.split(/(?<=[.!?])\s+/).length).toBeLessThanOrEqual(3);
  await expect(page.locator("#idea .learn-goals li")).toHaveCount(2);
});

test("the animation comes before the code, with the worked example as numbered steps beside it", async ({ page }) => {
  await page.goto(LESSON);
  const top = async (sel: string) => page.locator(sel).evaluate((e) => e.getBoundingClientRect().top + scrollY);
  expect(await top("#experiment")).toBeLessThan(await top("#code"));
  const follow = page.locator("#experiment .follow-along li");
  expect(await follow.count()).toBeGreaterThanOrEqual(3);
  await expect(page.locator("#code .code-side")).toContainText("Time");
  await expect(page.locator("#code pre")).toBeVisible();
});

test("the pattern is one compact card and the long explanations wait under Go deeper", async ({ page }) => {
  await page.goto(LESSON);
  await expect(page.locator("#pattern .insight")).toBeVisible();
  await expect(page.locator("#pattern .pitfall-card")).toContainText(/nested loops/i);
  const deeper = page.locator("#pattern details.go-deeper");
  await expect(deeper).toHaveCount(1);
  expect(await deeper.evaluate((d) => (d as HTMLDetailsElement).open)).toBe(false);
  await deeper.locator("summary").click();
  await expect(deeper).toContainText("Why growth beats milliseconds");
});

test("the execution transcript reads cleanly and the page fits a phone", async ({ page }) => {
  await page.goto(LESSON);
  await page.locator(".trace-transcript summary").click();
  await expect(page.locator(".trace-transcript li").first()).not.toContainText("Values: .");
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto(LESSON);
  await expect(page.locator("h1")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
