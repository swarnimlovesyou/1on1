import { test, expect } from "@playwright/test";

test("the hero leads with the promise, two actions and what you get", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1, name: /Make it click/ })).toBeVisible();
  const nav = page.getByRole("navigation", { name: "Site" });
  for (const [name, href] of [["Learn", "/learn"], ["Practise", "/practice"], ["Prep", "/prep"], ["Contests", "/contests"]] as const)
    await expect(nav.getByRole("link", { name, exact: true })).toHaveAttribute("href", href);
  await expect(page.getByRole("link", { name: "Start learning" }).first()).toHaveAttribute("href", "/learn");
  await expect(page.getByRole("link", { name: "Open your first notebook" })).toBeVisible();
  await expect(page.locator(".land-checks li")).toHaveCount(4);
});

test("the product is shown working: a live animation, a sheet row with companies, and a path you can switch", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".land-frame .experiment-top")).toBeVisible();
  await expect(page.locator(".land-frame .asked-at")).toContainText("Asked at");
  await page.getByRole("tab", { name: "Preparing for placements" }).click();
  await expect(page.getByRole("tabpanel")).toContainText(/Blind 75|mock/i);
  await page.getByRole("tab", { name: "New to DSA" }).click();
  await expect(page.getByRole("tabpanel")).toContainText(/Arrays/);
});

test("a real drill question can be checked on the landing page, and contests are live", async ({ page }) => {
  await page.goto("/");
  const drill = page.locator(".land-drill");
  await expect(drill.locator(".land-drill-prompt")).not.toBeEmpty();
  await drill.getByRole("textbox", { name: "Your answer" }).fill("-1");
  await drill.getByRole("button", { name: "Check" }).click();
  await expect(drill.getByRole("status")).toContainText(/Not quite|Correct/);
  await expect(page.locator(".land-contests li").first()).toBeVisible();
});

test("the key map answers a key press with what it opens", async ({ page }) => {
  await page.goto("/");
  const map = page.locator(".land-keys");
  await map.getByRole("button", { name: /^C\b/ }).click();
  await expect(map.locator(".land-key-detail")).toContainText("Contests");
});

test("the page still renders its promise and actions when the API is down", async ({ page }) => {
  await page.route("**/api/v1/**", (route) => route.fulfill({ status: 503, json: { message: "down" } }));
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.getByRole("link", { name: "Start learning" }).first()).toBeVisible();
});

test("a returning learner can sign in, and the page fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/");
  await expect(page.getByRole("link", { name: "Sign in" }).first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
