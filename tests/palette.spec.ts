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
