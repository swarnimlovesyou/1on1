import { expect, it } from "vitest";
import { editorTheme } from "./editorTheme";

it("follows the app theme, and the system setting when the app follows the system", () => {
  expect(editorTheme("light", true)).toBe("1on1-paper");
  expect(editorTheme("dark", false)).toBe("1on1-night");
  expect(editorTheme("system", true)).toBe("1on1-night");
  expect(editorTheme("system", false)).toBe("1on1-paper");
});
