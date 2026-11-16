import { test, expect } from "@playwright/test";
test("guest can learn, manipulate a trace, and open practice", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Make it click/ }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Open your first notebook" }).click();
  await expect(
    page.getByRole("heading", { name: "Make the idea click." }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: /Open Fixed-Size Sliding Window/ })
    .first()
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Fixed-Size Sliding Window",
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Next step" })).toBeEnabled();
  await page.getByRole("button", { name: "Next step" }).click();
  await expect(page.locator(".step-count")).toContainText("2");
  await page
    .getByRole("button", {
      name: /7: subtract 2 and add 1/,
    })
    .click();
  await page
    .getByRole("button", { name: "Check my intuition" })
    .first()
    .click();
  await expect(page.locator(".challenge-feedback")).toContainText(
    "You connected the state to the idea",
  );
  await page
    .locator(".related-problems")
    .getByRole("link", { name: "Three-reading window" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Three-reading window" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Submit", exact: true }),
  ).toBeVisible();
});
test("student account saves notes, creates a plan, and persists across reload", async ({
  page,
}) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Browser Verification");
  await page
    .getByLabel("Email address")
    .fill(`browser-${Date.now()}@example.test`);
  await page
    .getByLabel("Password", { exact: true })
    .fill("browser-test-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await expect(page).toHaveURL(/onboarding/);
  await page
    .getByRole("button", { name: "Find my first lightbulb moment" })
    .click();
  await expect(page).toHaveURL(/home/);
  await page.goto("/notebook");
  await page.getByRole("button", { name: "Capture a thought" }).click();
  await page.getByLabel("A name for this thought").fill("A window invariant");
  await page
    .getByLabel("In your own words")
    .fill("Only the entering and leaving values need work.");
  await page.getByRole("button", { name: "Save to notebook" }).click();
  await expect(
    page.getByRole("heading", { name: "A window invariant" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "A window invariant" }),
  ).toBeVisible();
  await page.goto("/plan");
  await page.getByRole("button", { name: "Build my practice plan" }).click();
  await expect(page.getByText("2 of 2 topics covered")).toBeVisible();
  await page.goto("/cohorts");
  await page.getByLabel("Cohort name").fill("Browser study circle");
  await page.getByRole("button", { name: "Create cohort" }).click();
  await expect(
    page.getByRole("heading", { name: "Browser study circle" }),
  ).toBeVisible();
});
test("desktop and mobile surfaces remain readable without overflow", async ({
  page,
}) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/home");
  await expect(page.locator(".continue-section a.button")).toHaveAttribute(
    "href",
    "/learn/lesson-complexity",
  );
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const route of [
      "/home",
      "/learn/lesson-sliding-window",
      "/practice",
      "/login",
    ]) {
      await page.goto(route);
      await expect(page.locator("h1").first()).toBeVisible({ timeout: 15000 });
      await page.waitForLoadState("networkidle");
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth + 1,
        ),
      ).toBeTruthy();
      await page.screenshot({
        path: `.impeccable/review/${width === 1440 ? "desktop" : "mobile"}${route === "/home" ? "" : "-" + route.split("/").at(-1)}.png`,
        fullPage: true,
      });
    }
  }
  expect(errors).toEqual([]);
});
test("draft and notebook position survive a fresh page load", async ({
  page,
}) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Saved work verification");
  await page
    .getByLabel("Email address")
    .fill(`saved-${Date.now()}@example.test`);
  await page
    .getByLabel("Password", { exact: true })
    .fill("browser-test-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page
    .getByRole("button", { name: "Find my first lightbulb moment" })
    .click();
  await expect(page).toHaveURL(/home/);
  await page.goto("/learn/lesson-sliding-window");
  await expect(page.getByRole("button", { name: "Next step" })).toBeEnabled();
  await page.getByRole("button", { name: "Next step" }).click();
  await page.getByRole("button", { name: "Next step" }).click();
  await expect
    .poll(async () => {
      const response = await page.request.get("/api/v1/progress");
      return (await response.json()).resumeStep;
    })
    .toBe(2);
  await page.reload();
  await expect(page.locator(".step-count")).toContainText("3");
  await page.goto("/practice/problem-running-altitude");
  await expect(page.locator(".monaco-editor").first()).toBeVisible();
  await page.locator(".monaco-editor textarea").first().focus();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.type("// A persisted Java solution\n");
  await expect(page.getByText("Saved automatically")).toBeVisible();
  await page.getByLabel("Coding language").selectOption("python");
  await page.getByLabel("Coding language").selectOption("java");
  await expect(
    page.getByText("// A persisted Java solution", { exact: false }).first(),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByText("// A persisted Java solution", { exact: false }).first(),
  ).toBeVisible();
});
