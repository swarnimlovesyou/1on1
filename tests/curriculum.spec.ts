import { test, expect } from "@playwright/test";
import type { CurriculumManifest, Lesson } from "../src/types";

test("all core notebooks expose real curriculum content and canonical references", async ({
  page,
}) => {
  test.setTimeout(120000);
  const curriculum = (await (
    await page.request.get("/api/v1/curriculum")
  ).json()) as CurriculumManifest;
  const lessons = (await (
    await page.request.get("/api/v1/lessons")
  ).json()) as Lesson[];
  expect(curriculum.concepts).toHaveLength(24);
  expect(curriculum.questions).toHaveLength(47);
  expect(lessons).toHaveLength(33);
  expect(
    curriculum.concepts
      .flatMap((c) => c.applications)
      .filter((a) => a.questionId === "leetcode-206"),
  ).toHaveLength(2);
  for (const concept of curriculum.concepts) {
    const lesson = lessons.find((l) => l.id === concept.lessonIds[0])!;
    expect(
      (lesson.teaching as unknown as { checkpoint: { answer?: number } })
        .checkpoint.answer,
    ).toBeUndefined();
    await page.goto("/learn/" + lesson.id);
    await expect(
      page.getByRole("heading", { name: lesson.title, exact: true, level: 1 }),
    ).toBeVisible();
    // a lesson may teach its own code when its animation runs more than the concept's example (Merge Sort)
    await expect(page.locator("#code pre")).toContainText(
      (lesson.teaching?.java ?? concept.java).implementation.split("\n")[0],
    );
    await expect(
      page
        .locator("#practice")
        .getByRole("heading", { name: "Apply this concept" }),
    ).toBeVisible();
    expect(lesson.experiment).toBeTruthy();
    await expect(page.locator('.lab-model')).toBeVisible();
    await expect(page.getByRole('button',{name:'Next step'})).toBeEnabled();
  }
});

test("new interactive lesson saves notes and location without inflated activity", async ({
  page,
}) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Curriculum verification");
  await page
    .getByLabel("Email address")
    .fill(`curriculum-${Date.now()}@example.test`);
  await page
    .getByLabel("Password", { exact: true })
    .fill("curriculum-verification-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page
    .getByRole("button", { name: "Find my first lightbulb moment" })
    .click();
  await page.goto("/learn/lesson-arrays");
  await page
    .getByRole("link", { name: "Its code", exact: true })
    .click();
  await page
    .getByLabel("Personal lesson note")
    .fill("The total covers the consumed prefix.");
  await page.getByRole("button", { name: "Save thought" }).click();
  await expect
    .poll(async () => {
      const progress = await (
        await page.request.get("/api/v1/progress")
      ).json();
      return progress.studyContexts.find(
        (c: { lesson: string }) => c.lesson === "lesson-arrays",
      )?.section;
    })
    .toBe("code");
  await page.reload();
  const progress = await (await page.request.get("/api/v1/progress")).json();
  expect(
    progress.notes.some(
      (n: { text: string }) =>
        n.text === "The total covers the consumed prefix.",
    ),
  ).toBeTruthy();
  expect(
    progress.studyContexts.find(
      (c: { lesson: string }) => c.lesson === "lesson-arrays",
    ).scene,
  ).toMatchObject({algorithm:'arrays',input:'2,1,5',seed:42});
  expect(progress.activity).toEqual({});
  const external = page.locator(
    '#practice a[href="https://leetcode.com/problems/running-sum-of-1d-array/"]',
  );
  await expect(external).toHaveAttribute("rel", "noopener noreferrer");
});

test("new worked specifications and corrected DFS fit mobile and desktop", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  for (const slug of ["matrices", "dfs"]) {
    await page.goto("/learn/lesson-" + slug);
    await expect(page.locator("#code pre")).toBeVisible();
    if (slug === "dfs") {
      await expect(
        page.getByRole("button", { name: "Next step" }),
      ).toBeEnabled();
      await page.getByRole("slider", { name: "Execution step" }).fill("3");
    }
    await page.locator("#experiment").scrollIntoViewIfNeeded();
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.screenshot({
        path: `.impeccable/review/curriculum-${slug}-${width}.png`,
      });
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth + 1,
        ),
      ).toBeTruthy();
    }
  }
  expect(errors).toEqual([]);
});
