import { test, expect } from "@playwright/test";

test("Ctrl+K jumps anywhere by keyboard and Escape closes it", async ({ page }) => {
  await page.goto("/home");
  await page.keyboard.press("Control+k");
  const dialog = page.getByRole("dialog", { name: "Jump to" });
  await expect(dialog).toBeVisible();
  await page.keyboard.type("puzzles");
  await expect(dialog.getByRole("option").first()).toContainText("Puzzles");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/prep\/puzzles$/);
  await expect(dialog).toBeHidden();
  await page.keyboard.press("Control+k");
  await page.keyboard.type("binary search");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("ArrowUp");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/learn\/lesson-binary-search$/);
  await page.keyboard.press("Control+k");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog", { name: "Jump to" })).toBeHidden();
});

test("the sidebar groups pages and links straight to sheets and animations", async ({ page }) => {
  await page.goto("/home");
  const nav = page.getByRole("navigation", { name: "Main navigation" });
  for (const group of ["Learn", "Practise", "Your work"]) await expect(nav.getByText(group, { exact: true })).toBeVisible();
  await expect(nav.getByRole("link", { name: "Animations" })).toHaveAttribute("href", "/learn/animations");
  await expect(nav.getByRole("link", { name: "Sheets" })).toHaveAttribute("href", "/practice?tab=sheets");
  await expect(page.getByRole("button", { name: /Jump to anything/ })).toBeVisible();
});

test("the palette keeps focus inside, closes with Escape after tabbing, and gives focus back", async ({ page }) => {
  await page.goto("/home");
  const trigger = page.getByRole("button", { name: /Jump to anything/ });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Jump to" });
  await expect(dialog).toBeVisible();
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");
  expect(await dialog.evaluate((d) => d.contains(document.activeElement))).toBeTruthy();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
  await expect(page.getByRole("combobox", { name: /Search pages/ })).toHaveCount(0);
});

test("text that matches no page still searches the library", async ({ page }) => {
  await page.goto("/home");
  await page.keyboard.press("Control+k");
  await expect(page.getByRole("combobox", { name: /Search pages/ })).toHaveAttribute("aria-expanded", "true");
  await page.keyboard.type("sliding window maximum");
  await expect(page.getByRole("option").last()).toContainText('Search the library for "sliding window maximum"');
  await page.getByRole("option").last().click();
  await expect(page).toHaveURL(/\/learn\?q=sliding/);
});

test("the performance lab is gone from navigation and search", async ({ page }) => {
  await page.goto("/home");
  await expect(page.getByRole("navigation", { name: "Main navigation" }).getByRole("link", { name: /Performance lab/ })).toHaveCount(0);
  await page.keyboard.press("Control+k");
  await page.keyboard.type("performance lab");
  await expect(page.getByRole("option", { name: /Performance lab/ })).toHaveCount(0);
});
