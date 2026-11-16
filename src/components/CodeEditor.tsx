import { useEffect } from "react";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor/esm/vs/editor/editor.api";
import "monaco-editor/esm/vs/basic-languages/java/java.contribution";
import "monaco-editor/esm/vs/basic-languages/python/python.contribution";
import "monaco-editor/esm/vs/basic-languages/cpp/cpp.contribution";
import EditorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import { useApp } from "../context";
import { editorTheme } from "./editorTheme";
self.MonacoEnvironment = { getWorker: () => new EditorWorker() };
loader.config({ monaco });
export default function CodeEditor({
  value,
  onChange,
  language,
}: {
  value: string;
  onChange: (s: string) => void;
  language: string;
}) {
  const { theme } = useApp();
  const name = editorTheme(
    theme,
    matchMedia("(prefers-color-scheme: dark)").matches,
  );
  useEffect(() => {
    // the page's CSS variables don't reach Monaco, so the paper and night palettes are repeated here
    monaco.editor.defineTheme("1on1-paper", {
      base: "vs",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#FFFFFF",
        "editor.foreground": "#1F2430",
        "editorLineNumber.foreground": "#9A9DA6",
        "editor.lineHighlightBackground": "#F6F4EE",
        "editorCursor.foreground": "#2F4A6E",
        "editor.selectionBackground": "#D5DEEA",
      },
    });
    monaco.editor.defineTheme("1on1-night", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#1E2024",
        "editor.foreground": "#ECE8DF",
        "editorLineNumber.foreground": "#6E6B65",
        "editor.lineHighlightBackground": "#25282D",
        "editorCursor.foreground": "#A9BEDC",
        "editor.selectionBackground": "#34404F",
      },
    });
  }, []);
  return (
    <Editor
      height="440px"
      language={language === "cpp" ? "cpp" : language}
      value={value}
      onChange={(v) => onChange(v ?? "")}
      theme={name}
      loading={
        <textarea
          aria-label="Code editor loading"
          className="code-fallback"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      }
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        fontFamily: "JetBrains Mono",
        lineHeight: 25,
        padding: { top: 18, bottom: 18 },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 4,
        wordWrap: "on",
        accessibilitySupport: "on",
      }}
    />
  );
}
