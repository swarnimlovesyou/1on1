import { test, expect } from "@playwright/test";

test("a learner pairs an assistant, the token works once shown, and revoking stops it", async ({ page }) => {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Pairing check");
  await page.getByLabel("Email address").fill(`pairing-${Date.now()}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill("pairing-check-password");
  await page.getByRole("button", { name: "Create your account" }).click();
  await page.getByRole("button", { name: "Find my first lightbulb moment" }).click();
  await page.goto("/settings");
  await page.getByLabel("Assistant or device").fill("Test laptop");
  await page.getByRole("button", { name: "Make a token" }).click();
  const config = await page.locator(".pairing-token pre").innerText();
  const token = JSON.parse(config).mcpServers["1on1"].env.ONEONONE_TOKEN as string;
  const context = await page.request.get("/api/v1/assistant/context", { headers: { authorization: "Bearer " + token } });
  expect(context.status()).toBe(200);
  expect((await context.json()).name).toBe("Pairing check");
  await page.getByRole("button", { name: "Revoke Test laptop" }).click();
  await expect(page.locator(".pairing-list li")).toHaveCount(0);
  expect((await page.request.get("/api/v1/assistant/context", { headers: { authorization: "Bearer " + token } })).status()).toBe(401);
});
