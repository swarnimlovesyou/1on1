import { test, expect } from "@playwright/test";

test("aptitude and reasoning list their guides, each with a drill", async ({ page }) => {
  await page.goto("/prep/aptitude");
  await expect(page.locator(".prep-guides li")).toHaveCount(8);
  await expect(page.locator(".prep-guides li").getByRole("link", { name: "Practise" })).toHaveCount(8);
  await page.goto("/prep/reasoning");
  await expect(page.locator(".prep-guides li")).toHaveCount(5);
});

test("a guest drills a topic: wrong answer shows the expected one, Next brings a new question", async ({ page }) => {
  await page.goto("/prep/drill/percentages");
  const prompt = page.locator(".drill-prompt");
  await expect(prompt).toBeVisible();
  const first = await prompt.textContent();
  await page.getByRole("textbox", { name: "Your answer" }).fill("-1");
  await page.getByRole("button", { name: "Check" }).click();
  const feedback = page.getByRole("status");
  await expect(feedback).toContainText("Not quite");
  await expect(feedback).toContainText("The answer is");
  await expect(page.locator(".drill-streak")).toContainText("0");
  await page.getByRole("button", { name: "Next question" }).click();
  await expect(prompt).not.toHaveText(first ?? "");
  await expect(page.getByRole("textbox", { name: "Your answer" })).toHaveValue("");
});

test("the percentages guide links to its drill", async ({ page }) => {
  await page.goto("/prep/guide/guide-aptitude-percentages");
  await page.getByRole("link", { name: /Practise with unlimited questions/ }).click();
  await expect(page).toHaveURL(/\/prep\/drill\/percentages$/);
  await expect(page.locator(".drill-prompt")).toBeVisible();
});

test("a syllogism drill offers four choices and fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/prep/drill/syllogisms");
  await expect(page.locator(".drill-prompt")).toBeVisible();
  await expect(page.locator(".checkpoint-options button")).toHaveCount(4);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});

test("an unknown drill topic says so", async ({ page }) => {
  await page.goto("/prep/drill/calculus");
  await expect(page.getByText("That drill topic doesn't exist.")).toBeVisible();
});
