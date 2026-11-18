import { test, expect } from "@playwright/test";

test("the app is light only, in Geist, even for a learner who had dark mode saved", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("1on1-theme", "dark"));
  await page.goto("/home");
  await expect(page.getByRole("button", { name: /Toggle color theme/ })).toHaveCount(0);
  const look = await page.evaluate(() => {
    const s = getComputedStyle(document.body);
    return { bg: s.backgroundColor, font: s.fontFamily, theme: document.documentElement.dataset.theme ?? "" };
  });
  expect(look.bg).toBe("rgb(244, 246, 245)");
  expect(look.font).toMatch(/^"?Geist Variable/);
  expect(look.theme).not.toBe("dark");
});

test("intermediate widths keep the notebook usable", async ({ page }) => {
  for (const width of [1440, 1024, 768, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto("/learn/lesson-sliding-window");
    await expect(page.getByRole("heading", { name: "Fixed-Size Sliding Window", level: 1 })).toBeVisible();
    await expect(page.getByRole("button", { name: "Next step" })).toBeEnabled();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
  }
});
