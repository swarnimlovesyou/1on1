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

test("a failed question load offers a retry and a way back", async ({ page }) => {
  let failed = false;
  await page.route("**/api/v1/drills/averages/next*", (route) => {
    if (failed) return route.continue();
    failed = true;
    return route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ message: "Service unavailable." }) });
  });
  await page.goto("/prep/drill/averages");
  await expect(page.getByRole("link", { name: "Back to the guide" })).toBeVisible();
  await page.getByRole("button", { name: /try again/i }).click();
  await expect(page.locator(".drill-prompt")).toBeVisible();
});

test("syllogism statements and conclusions are on separate lines, and a percent answer reads 15%", async ({ page }) => {
  await page.goto("/prep/drill/syllogisms");
  const text = await page.locator(".drill-prompt").innerText();
  expect(text.split("\n").length).toBeGreaterThanOrEqual(4);
  await page.route("**/api/v1/drills/percentages/next*", (r) => r.fulfill({ json: { topic: "percentages", seed: 7, prompt: "45 is what percent of 300?", unit: "%" } }));
  await page.route("**/api/v1/drills/percentages/answer", (r) => r.fulfill({ json: { correct: false, expected: "15", explanation: "45 ÷ 300 × 100 = 15%." } }));
  await page.goto("/prep/drill/percentages");
  await page.getByRole("textbox", { name: "Your answer" }).fill("1");
  await page.getByRole("button", { name: "Check" }).click();
  await expect(page.getByRole("status")).toContainText("The answer is 15%.");
});

test("coming back to a drill brings a fresh question", async ({ page }) => {
  let n = 0;
  await page.route("**/api/v1/drills/averages/next*", (r) => r.fulfill({ json: { topic: "averages", seed: ++n, prompt: `Question ${n}` } }));
  await page.goto("/prep/drill/averages");
  await expect(page.locator(".drill-prompt")).toHaveText("Question 1");
  await page.getByRole("link", { name: /Back to/ }).click();
  // leave only once the guide is on screen, as a learner would; an instant back cancels the navigation
  await expect(page.locator(".prep-guide h1")).toBeVisible();
  await page.goBack();
  await expect(page.locator(".drill-prompt")).toHaveText("Question 2");
});
