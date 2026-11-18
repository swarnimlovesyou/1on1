import { test, expect } from "@playwright/test";

test("a quiz-style mock runs one question at a time on a timer and ends with a section score and review", async ({ page }) => {
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
