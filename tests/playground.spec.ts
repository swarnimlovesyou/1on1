import { test, expect } from "@playwright/test";

test("the system design track links to the traffic playground, which says it is a teaching model", async ({ page }) => {
  await page.goto("/prep/system-design");
  await page.getByRole("link", { name: /Traffic playground/ }).click();
  await expect(page).toHaveURL(/\/prep\/system-design\/playground$/);
  await expect(page.getByText(/teaching model, not a capacity planner/)).toBeVisible();
});

test("overloading the servers drops requests and names them; adding servers relieves it", async ({ page }) => {
  await page.goto("/prep/system-design/playground");
  const rate = page.getByRole("slider", { name: "Requests per second" });
  await rate.focus();
  await page.keyboard.press("End");
  await expect(page.locator(".playground-bottleneck")).toContainText("App servers");
  await expect(page.locator('[data-metric="dropped"]')).not.toHaveText("0");
  const servers = page.getByRole("slider", { name: "App servers" });
  await servers.focus();
  await page.keyboard.press("End");
  await expect(page.locator(".playground-change")).toContainText("App servers");
  await expect(page.locator(".playground-bottleneck")).not.toContainText("App servers");
});

test("turning the cache on lowers the database load", async ({ page }) => {
  await page.goto("/prep/system-design/playground");
  const db = page.locator('[data-metric="dbUtil"]');
  const before = parseFloat((await db.textContent()) ?? "0");
  await page.getByRole("checkbox", { name: "Cache" }).check();
  await expect.poll(async () => parseFloat((await db.textContent()) ?? "0")).toBeLessThan(before);
});

test("the playground fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/prep/system-design/playground");
  await expect(page.locator("h1")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});

test("dropped requests carry a per-second unit and only the change sentence is announced", async ({ page }) => {
  await page.goto("/prep/system-design/playground");
  await expect(page.locator('[data-metric="dropped"]')).toHaveText(/\/s$/);
  await expect(page.locator(".playground-results")).not.toHaveAttribute("aria-live", /.+/);
  await expect(page.locator(".playground-change")).toHaveAttribute("aria-live", "polite");
});
