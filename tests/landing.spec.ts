import { test, expect } from "@playwright/test";

test("the hero sits in a framed landscape with a glass nav, a badge, the headline and a learn box", async ({ page }) => {
  await page.goto("/");
  const hero = page.locator(".meadow-hero");
  await expect(hero.locator("svg.meadow-landscape")).toBeVisible();
  await expect(hero.locator("image.meadow-photo")).toHaveAttribute("href", "/landing/meadow-grindelwald.jpg");
  expect((await page.request.get("/landing/meadow-grindelwald.jpg")).ok()).toBeTruthy();
  await expect(hero.getByRole("link", { name: /Georgi Kalaydzhiev/ })).toHaveAttribute("href", /unsplash\.com/);
  await expect(hero.getByRole("heading", { level: 1, name: /Make it click/ })).toBeVisible();
  const pill = hero.getByRole("navigation", { name: "Site" });
  for (const [name, href] of [["Learn", "/learn"], ["Practise", "/practice"], ["Prep", "/prep"], ["Sheets", "/practice?tab=sheets"]] as const)
    await expect(pill.getByRole("link", { name, exact: true })).toHaveAttribute("href", href);
  await expect(hero.locator(".meadow-badge")).toContainText(/1\d,\d{3}/);
  await hero.getByRole("textbox", { name: "What do you want to learn?" }).fill("binary search");
  await hero.getByRole("button", { name: "Start" }).click();
  await expect(page).toHaveURL(/\/learn\?q=binary(\+|%20)search$/);
});

test("below the hero: real figures, a live animation and three ways in", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".landing-figures")).toContainText("33");
  for (const [name, href] of [["Learn", "/learn"], ["Practise", "/practice"], ["Prep", "/prep"]] as const)
    await expect(page.locator(".ways-in").getByRole("link", { name: new RegExp("^" + name) })).toHaveAttribute("href", href);
  await expect(page.locator(".landing-demo .experiment-top")).toBeVisible();
});

test("the landing page fits a phone in both themes", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  for (const scheme of ["light", "dark"] as const) {
    await page.emulateMedia({ colorScheme: scheme });
    await page.goto("/");
    await expect(page.locator("h1")).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
  }
});

test("a returning learner can sign in from the landing page on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/");
  await expect(page.locator(".meadow-hero").getByRole("link", { name: "Sign in" })).toBeVisible();
});
