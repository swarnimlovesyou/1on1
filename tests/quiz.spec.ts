import { test, expect } from "@playwright/test";

test("a quiz-style mock runs one question at a time on a timer and ends with a section score and review", async ({ page }) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Quiz check");
  await page.getByLabel("Email address").fill(`quiz-${Date.now()}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill("quiz-check-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page.getByRole("button", { name: "Find my first lightbulb moment" }).click();
  await page.goto("/practice?tab=mock");
  await page.getByRole("tab", { name: "Quiz" }).click();
  await page.getByRole("button", { name: "Start the quiz" }).click();
  const runner = page.locator(".quiz-runner");
  await expect(runner.locator(".quiz-timer")).toContainText(/\d+:\d{2}/);
  await expect(runner.locator(".quiz-nav button")).toHaveCount(15);
  await expect(runner.locator(".quiz-question")).not.toBeEmpty();
  const options = runner.locator(".quiz-options button");
  if (await options.count()) await options.first().click();
  else await runner.getByRole("textbox", { name: "Your answer" }).fill("1");
  // the options are lettered A-D; pressing a letter must not navigate away and lose the quiz
  await runner.locator(".quiz-nav button").first().focus();
  await page.keyboard.press("a");
  await expect(page).toHaveURL(/tab=mock/);
  await expect(runner.locator(".quiz-nav button").first()).toHaveClass(/answered/);
  await runner.getByRole("button", { name: "Next" }).click();
  await expect(runner.locator(".quiz-nav button").nth(1)).toHaveClass(/current/);
  await runner.getByRole("button", { name: "Submit" }).click();
  await page.getByRole("button", { name: "Submit anyway" }).click();
  const result = page.locator(".quiz-result");
  await expect(result).toContainText(/\d+ of 15/);
  await expect(result.locator(".quiz-section-score")).toHaveCount(3);
  await expect(result.locator(".quiz-review li").first()).toContainText(/Correct|Answer/);
});

test("guests are asked to sign in before a timed quiz", async ({ page }) => {
  await page.goto("/practice?tab=mock");
  await expect(page.getByRole("heading", { name: "Sign in to take a timed quiz." })).toBeVisible();
});

test("a quiz in progress survives a page refresh with its answers and clock", async ({ page }) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Quiz refresh");
  await page.getByLabel("Email address").fill(`quiz-refresh-${Date.now()}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill("quiz-refresh-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page.getByRole("button", { name: "Find my first lightbulb moment" }).click();
  await page.goto("/practice?tab=mock");
  await page.getByRole("button", { name: "Start the quiz" }).click();
  const runner = page.locator(".quiz-runner");
  const first = await runner.locator(".quiz-question").innerText();
  const options = runner.locator(".quiz-options button");
  if (await options.count()) await options.first().click();
  else await runner.getByRole("textbox", { name: "Your answer" }).fill("1");
  await page.reload();
  await expect(runner.locator(".quiz-question")).toHaveText(first);
  await expect(runner.locator(".quiz-nav button").first()).toHaveClass(/answered/);
  await expect(runner.locator(".quiz-timer")).toContainText(/\d+:\d{2}/);
});
