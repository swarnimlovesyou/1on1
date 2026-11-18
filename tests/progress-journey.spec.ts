import { test, expect } from "@playwright/test";

test("progress shows what is done and where the learner is heading", async ({ page }) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Journey check");
  await page.getByLabel("Email address").fill(`journey-${Date.now()}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill("journey-check-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page.getByRole("button", { name: "Find my first lightbulb moment" }).click();
  await page.goto("/progress");
  await expect(page.getByRole("heading", { name: "Where you've been" })).toBeVisible();
  await expect(page.locator(".mastery-legend li")).toHaveCount(4);
  await expect(page.locator(".family-progress li").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Where you're heading" })).toBeVisible();
  await expect(page.locator(".journey-next")).toHaveAttribute("href", /\//);
  await expect(page.locator(".journey-frontier li").first()).toBeVisible();
});
