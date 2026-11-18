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
  await page.getByRole("tab", { name: /Quiz/ }).click();
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

test("a guide splits into notes, a quiz and sources, and prints as a PDF", async ({ page }) => {
  await page.goto("/prep/guide/guide-cs-fundamentals-os-deadlocks");
  await expect(page.getByRole("tab", { name: "Notes" })).toHaveAttribute("aria-selected", "true");
  await expect(page.locator(".prep-guide section h2").first()).toBeVisible();
  await expect(page.locator(".prep-cheatsheet li").first()).toBeVisible();
  await page.getByRole("tab", { name: /Quiz/ }).click();
  await expect(page).toHaveURL(/view=quiz/);
  await expect(page.locator(".prep-quiz .learning-challenge")).toHaveCount(5);
  await page.getByRole("tab", { name: "Sources" }).click();
  const links = page.locator(".prep-sources a");
  await expect(links.first()).toBeVisible();
  expect(await links.count()).toBeGreaterThanOrEqual(2);
  for (const href of await links.evaluateAll((a) => a.map((x) => (x as HTMLAnchorElement).href))) expect(href).toMatch(/^https?:\/\//);
  await expect(links.first()).toHaveAttribute("rel", /noopener/);
  await page.evaluate(() => ((window as unknown as { printed: number }).printed = 0, (window.print = () => (window as unknown as { printed: number }).printed++)));
  await page.getByRole("button", { name: "Save as PDF" }).click();
  expect(await page.evaluate(() => (window as unknown as { printed: number }).printed)).toBe(1);
  await expect(page.getByRole("tab", { name: "Notes" })).toHaveAttribute("aria-selected", "true");
});

test("a track has a reading list and a printable handbook of every guide", async ({ page }) => {
  await page.goto("/prep/cs-fundamentals");
  await expect(page.locator(".prep-reading a").first()).toBeVisible();
  await page.getByRole("link", { name: /handbook/i }).click();
  await expect(page).toHaveURL(/\/prep\/cs-fundamentals\/handbook$/);
  await expect(page.locator(".prep-handbook article")).toHaveCount(30);
  await expect(page.getByRole("button", { name: "Save as PDF" })).toBeVisible();
});
