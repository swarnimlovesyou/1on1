import { test, expect, type Page } from "@playwright/test";

// With no server runner (as on free hosting), Python's Run executes in the browser with Pyodide.
async function replaceCode(page: Page, code: string) {
  const editor = page.locator(".monaco-editor textarea").first();
  await editor.focus();
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Delete");
  await page.keyboard.insertText(code); // insertText skips the editor's auto-closing brackets
}

test("Python runs in the browser with the learner's input, and a runaway loop is stopped", async ({ page }) => {
  test.setTimeout(240000); // the first run downloads Pyodide from the CDN
  await page.route("**/api/v1/system", (r) => r.fulfill({ json: { name: "1on1", ai: false, execution: false } }));
  const problems = await (await page.request.get("/api/v1/problems")).json();
  await page.goto("/practice/" + problems[0].id);
  await page.getByLabel("Coding language").selectOption("python");
  await replaceCode(page, "a, b = map(int, input().split())\nprint(a + b)\n");
  await page.getByRole("button", { name: "Custom input" }).click();
  await page.getByLabel("Input for the Run button").fill("2 3");
  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(page.getByText("RAN IN BROWSER").first()).toBeVisible({ timeout: 180000 });
  await expect(page.getByText(/Ran in your browser with Python/)).toBeVisible();
  await page.locator("summary", { hasText: "Test 0" }).first().click();
  await expect(page.locator("pre", { hasText: /^5\s*$/ }).first()).toBeVisible();

  await replaceCode(page, "while True:\n    pass\n");
  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(page.getByText("TIME LIMIT EXCEEDED").first()).toBeVisible({ timeout: 30000 });
});
