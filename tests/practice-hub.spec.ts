import { test, expect } from "@playwright/test";

const CREDIT = "Company lists: community-reported (LeetCode company tags, 2022 snapshot), MIT © 2022 Huan Xu.";

test("the question bank filters external questions and credits its sources", async ({ page }) => {
  await page.goto("/practice?tab=bank");
  const rows = page.locator(".bank-table tbody tr");
  await expect(rows.first()).toBeVisible({ timeout: 15000 });
  await page.getByLabel("Source").selectOption("Codeforces");
  await page.getByLabel("Difficulty").selectOption("Hard");
  await expect(page.locator(".bank-table tbody tr").first()).toContainText("Codeforces");
  for (const text of await page.locator(".bank-table tbody tr .bank-source").allTextContents()) expect(text).toBe("Codeforces");
  const external = page.locator(".bank-table tbody tr a[target=_blank]").first();
  await expect(external).toHaveAttribute("rel", /noopener/);
  await page.goto("/practice?tab=bank&company=Google");
  await expect(page.getByText(CREDIT)).toBeVisible();
  await page.goto("/practice?tab=companies");
  await expect(page.getByRole("link", { name: /Google/ }).first()).toBeVisible();
});

test("a learner starts a mock, opens a problem with its timer and finishes with a report", async ({ page }) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Mock verification");
  await page.getByLabel("Email address").fill(`mock-${Date.now()}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill("mock-verification-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page.getByRole("button", { name: "Find my first lightbulb moment" }).click();
  await page.goto("/practice?tab=mock");
  await page.getByRole("combobox", { name: "Problems" }).selectOption("3");
  await page.getByRole("combobox", { name: "Time" }).selectOption("60");
  await page.getByRole("button", { name: "Start mock" }).click();
  await expect(page.locator(".mock-timer")).toBeVisible();
  const links = page.locator(".mock-problems a");
  await expect(links).toHaveCount(3);
  await expect(links.first()).toHaveAttribute("href", /\?mock=mock-/);
  await links.first().click();
  await expect(page.locator(".mock-banner")).toBeVisible();
  await page.goto("/practice?tab=mock");
  await page.getByRole("button", { name: "Finish now" }).click();
  await expect(page.locator(".mock-report")).toContainText("0 of 3");
});
