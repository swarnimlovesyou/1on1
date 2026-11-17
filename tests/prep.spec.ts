import { test, expect } from "@playwright/test";

test("Prep lists five tracks and CS fundamentals guides by subject", async ({ page }) => {
  await page.goto("/prep");
  await expect(page.locator(".prep-track")).toHaveCount(5);
  await page.getByRole("link", { name: /CS fundamentals/ }).click();
  for (const subject of ["OOP", "DBMS", "Operating systems", "Computer networks", "SQL"])
    await expect(page.getByRole("heading", { name: subject, exact: true })).toBeVisible();
  await expect(page.locator(".prep-guides li")).toHaveCount(30);
});

test("a guide shows its sections and a five-question quiz that grades on the server", async ({ page }) => {
  await page.goto("/prep/cs-fundamentals");
  await page.locator(".prep-guides a").first().click();
  await expect(page.locator(".prep-guide h1")).toBeVisible();
  await expect(page.locator(".prep-guide section h2").first()).toBeVisible();
  const cards = page.locator(".prep-quiz .learning-challenge");
  await expect(cards).toHaveCount(5);
  const first = cards.first();
  await first.locator(".checkpoint-options button").first().click();
  await first.locator(".challenge-actions button").first().click();
  await expect(first.locator(".challenge-feedback")).toBeVisible();
});

test("Prep fits a phone without sideways scrolling", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  for (const url of ["/prep", "/prep/cs-fundamentals"]) {
    await page.goto(url);
    await expect(page.locator("h1").first()).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
  }
  await page.locator(".prep-guides a").first().click();
  await expect(page.locator(".prep-guide h1")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});
