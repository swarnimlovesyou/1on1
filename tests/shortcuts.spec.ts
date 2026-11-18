import { test, expect } from "@playwright/test";

test("single keys jump between areas, and the sidebar shows each key", async ({ page }) => {
  await page.goto("/home");
  await expect(page.locator(".app-main, main").first()).toBeVisible();
  await page.keyboard.press("p");
  await expect(page).toHaveURL(/\/practice$/);
  await page.keyboard.press("c");
  await expect(page).toHaveURL(/\/contests$/);
  await page.keyboard.press("r");
  await expect(page).toHaveURL(/\/prep$/);
  await page.keyboard.press("h");
  await expect(page).toHaveURL(/\/home$/);
  const nav = page.getByRole("navigation", { name: "Main navigation" });
  await expect(nav.getByRole("link", { name: /Practice/ }).locator("kbd")).toHaveText("P");
});

test("typing in a field never jumps away", async ({ page }) => {
  await page.goto("/practice?tab=bank");
  const search = page.getByRole("textbox", { name: "Search the question bank" });
  await search.click();
  await page.keyboard.type("prc");
  await expect(page).toHaveURL(/tab=bank/);
  await expect(search).toHaveValue("prc");
});

test("? lists the shortcuts and Escape closes the list", async ({ page }) => {
  await page.goto("/home");
  await page.keyboard.press("Shift+?");
  const dialog = page.getByRole("dialog", { name: "Keyboard shortcuts" });
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText("Contests");
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
});
