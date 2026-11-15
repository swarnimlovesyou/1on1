import { test, expect } from "@playwright/test";

const journeys = [
  {
    algorithm: "sliding-window",
    choice: 1,
    fields: {
      "Left index": "1",
      "Right index": "3",
      "Current sum": "7",
      "Best full-window sum": "8",
    },
  },
  {
    algorithm: "bst",
    choice: 2,
    fields: {
      "Just-inserted key": "6",
      "Root key": "8",
      "Height in nodes": "3",
    },
  },
  {
    algorithm: "bfs",
    choice: 0,
    fields: {
      "Currently processing vertex": "0",
      "Just-discovered vertex": "2",
      "Queue, front to back": "1,2",
    },
  },
  {
    algorithm: "tabulation",
    choice: 1,
    fields: { "Destination index": "5", "Stored value": "5" },
  },
];
for (const journey of journeys)
  test(`${journey.algorithm}: real prediction and dry-run grading`, async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto("/learn/lesson-" + journey.algorithm);
    await expect(page.getByRole("button", { name: "Next step" })).toBeEnabled();
    const prediction = page.locator(
      `[aria-labelledby="challenge-${journey.algorithm}-prediction"]`,
    );
    await prediction
      .locator(".checkpoint-options button")
      .nth(journey.choice)
      .click();
    await prediction
      .getByRole("button", { name: "Check my intuition" })
      .click();
    await expect(prediction.getByRole("status")).toContainText(
      "You connected the state",
    );
    const dry = page.locator(
      `[aria-labelledby="challenge-${journey.algorithm}-dry-run"]`,
    );
    for (const [label, value] of Object.entries(journey.fields))
      await dry.getByLabel(label, { exact: true }).fill(value);
    await dry.getByRole("button", { name: "Check my dry run" }).click();
    await expect(dry.getByRole("status")).toContainText(
      "matches the Java execution",
    );
    await expect(page.locator(".related-problems a")).toHaveCount(2);
    await page.getByRole("slider", { name: "Execution step" }).fill("3");
    await page
      .locator("#experiment")
      .evaluate((element) => element.scrollIntoView({ block: "start" }));
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.screenshot({
        path: `.impeccable/review/phase1-${journey.algorithm}-${width}.png`,
      });
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth + 1,
        ),
      ).toBeTruthy();
    }
    expect(errors).toEqual([]);
  });

test("custom input, exact step, and meaningful activity survive reload", async ({
  page,
}) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Reference journey verification");
  await page
    .getByLabel("Email address")
    .fill(`reference-${Date.now()}@example.test`);
  await page
    .getByLabel("Password", { exact: true })
    .fill("reference-journey-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page
    .getByRole("button", { name: "Find my first lightbulb moment" })
    .click();
  await page.goto("/learn/lesson-sliding-window");
  await page.getByLabel("Your input", { exact: true }).fill("4,4,4,1");
  await page.getByRole("button", { name: "Update experiment" }).click();
  await page.getByRole("slider", { name: "Execution step" }).fill("3");
  await expect
    .poll(async () => {
      const response = await page.request.get("/api/v1/progress");
      const data = await response.json();
      return data.studyContexts?.find(
        (item: { lesson: string }) => item.lesson === "lesson-sliding-window",
      )?.scene.input;
    })
    .toBe("4,4,4,1");
  await expect
    .poll(async () => {
      const response = await page.request.get("/api/v1/progress");
      return (await response.json()).resumeStep;
    })
    .toBe(3);
  expect(
    (await (await page.request.get("/api/v1/progress")).json()).activity,
  ).toEqual({});
  await page.reload();
  await expect(page.getByLabel("Your input", { exact: true })).toHaveValue(
    "4,4,4,1",
  );
  await expect(
    page.getByRole("slider", { name: "Execution step" }),
  ).toHaveValue("3");
  const challenge = page.locator(
    '[aria-labelledby="challenge-sliding-window-manipulation"]',
  );
  await challenge.getByRole("button", { name: "Check this input" }).click();
  await expect(challenge.getByRole("status")).toContainText(
    "You connected the state",
  );
  await page.reload();
  await expect(challenge.getByText("Previously passed")).toBeVisible();
});

test("reduced motion and rapid seeking retain correct controls and state", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/learn/lesson-tabulation");
  await page.getByRole("button", { name: "Play animation" }).click();
  await page.getByRole("slider", { name: "Execution step" }).fill("2");
  await expect(
    page.getByRole("button", { name: "Play animation" }),
  ).toBeVisible();
  await expect(
    page.getByRole("slider", { name: "Execution step" }),
  ).toHaveValue("2");
  await page.getByRole("slider", { name: "Execution step" }).fill("0");
  await page.locator(".experiment").focus();
  await page.keyboard.press("ArrowRight");
  await expect(
    page.getByRole("slider", { name: "Execution step" }),
  ).toHaveValue("1");
  await page.keyboard.press("Home");
  await expect(
    page.getByRole("slider", { name: "Execution step" }),
  ).toHaveValue("0");
});

test("tutor history recovers from a failed load and stays scoped to its lesson", async ({
  page,
}) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Tutor history verification");
  await page
    .getByLabel("Email address")
    .fill(`history-${Date.now()}@example.test`);
  await page
    .getByLabel("Password", { exact: true })
    .fill("history-verification-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page
    .getByRole("button", { name: "Find my first lightbulb moment" })
    .click();
  const session = await (await page.request.get("/api/v1/auth/session")).json();
  const saved = await page.request.put("/api/v1/conversations/lesson-bfs", {
    headers: { "X-CSRF-TOKEN": session.csrf },
    data: { messages: [{ role: "you", text: "My saved frontier question" }] },
  });
  expect(saved.ok()).toBeTruthy();
  await page.route("**/api/v1/conversations/lesson-bfs", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ message: "Temporary history outage" }),
    });
    await page.unroute("**/api/v1/conversations/lesson-bfs");
  });
  await page.goto("/learn/lesson-bfs");
  await page.getByRole("button", { name: "Ask 1on1" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Temporary history outage",
  );
  await page.getByRole("button", { name: "Retry conversation" }).click();
  await expect(
    page.getByText("My saved frontier question", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await page.getByRole("button", { name: "Ask 1on1" }).click();
  await expect(
    page.getByText("My saved frontier question", { exact: true }),
  ).toBeVisible();
  await page.goto("/learn/lesson-bst");
  await page.getByRole("button", { name: "Ask 1on1" }).click();
  await expect(
    page.getByRole("button", { name: "Give me a hint without the solution" }),
  ).toBeEnabled();
  await expect(
    page.getByText("My saved frontier question", { exact: true }),
  ).toHaveCount(0);
});
