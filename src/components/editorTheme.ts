/** Which Monaco theme matches the app's light, dark or system setting. Kept apart from Monaco so it can be tested. */
export function editorTheme(
  theme: string,
  prefersDark: boolean,
): "1on1-paper" | "1on1-night" {
  return theme === "dark" || (theme === "system" && prefersDark)
    ? "1on1-night"
    : "1on1-paper";
}
