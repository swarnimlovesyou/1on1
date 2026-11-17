import { test, expect } from "@playwright/test";

test("a failed LeetCode refresh never claims to have ticked sheet questions", async ({ page }) => {
  await page.route("**/api/v1/auth/session", (r) => r.fulfill({ json: { user: { id: "u1", name: "Test Learner", email: "t@example.test", role: "LEARNER" }, csrf: "x" } }));
  await page.route("**/api/v1/connections/leetcode", (r) =>
    r.request().method() === "POST"
      ? r.fulfill({ json: { username: "someone", status: "unavailable", sheetTicksAdded: 3, message: "LeetCode couldn't be reached." } })
      : r.fulfill({ json: { username: "someone", status: "synced", data: {} } }),
  );
  await page.goto("/settings");
  const refreshed = page.waitForResponse((r) => r.url().includes("/connections/leetcode") && r.request().method() === "POST");
  await page.getByRole("button", { name: "Refresh profile" }).click();
  await refreshed;
  const toast = page.locator(".toast");
  await expect(toast).toContainText("couldn't be reached");
  await expect(toast).not.toContainText("ticked");
});
