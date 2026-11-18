import { test, expect } from "@playwright/test";

test("the planner suggests a plan from the learner's record and builds it", async ({ page }) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Plan advisor");
  await page.getByLabel("Email address").fill(`advisor-${Date.now()}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill("plan-advisor-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page.getByRole("button", { name: "Find my first lightbulb moment" }).click();
  await page.goto("/plan");
  const panel = page.locator(".plan-advisor");
  await panel.getByLabel("Goal").selectOption("foundations");
  await panel.getByLabel("Weeks").selectOption("2");
  await panel.getByLabel("Time a day").selectOption("60");
  await panel.getByRole("button", { name: "Suggest my plan" }).click();
  await expect(panel.locator(".advisor-topics li").first()).toBeVisible();
  await expect(panel.locator(".advisor-reasons li").first()).toBeVisible();
  await expect(panel).toContainText(/Planned (with AI|from your record)/);
  await expect(panel).toContainText("Easy");
  await panel.getByRole("button", { name: "Build this plan" }).click();
  await expect(page.locator(".plan-result")).toContainText(/Foundations|Placement|week/i);
});
