import { test, expect } from "@playwright/test";

const signedIn = async (page: import("@playwright/test").Page) =>
  page.route("**/api/v1/auth/session", (r) => r.fulfill({ json: { user: { id: "u1", name: "Test Learner", email: "t@example.test", role: "LEARNER" }, csrf: "x" } }));

test("a signed-in learner reports where a question was asked", async ({ page }) => {
  await signedIn(page);
  let sent: unknown = null;
  await page.route("**/api/v1/reports", (r) => {
    sent = r.request().postDataJSON();
    return r.fulfill({ json: { saved: true, repeat: false } });
  });
  await page.goto("/practice/q/lc-two-sum");
  const form = page.getByRole("form", { name: "I was asked this" });
  await form.getByRole("textbox", { name: "Company" }).fill("Flipkart");
  await form.getByRole("radio", { name: "Interview" }).check();
  await form.getByRole("button", { name: "Report" }).click();
  await expect(form.getByRole("status")).toContainText("Thanks");
  expect(sent).toEqual({ questionId: "lc-two-sum", company: "Flipkart", stage: "Interview" });
});

test("a guest is asked to sign in before reporting", async ({ page }) => {
  await page.goto("/practice/q/lc-two-sum");
  await expect(page.getByText(/Sign in to report/)).toBeVisible();
});
