import { useEffect } from "react";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor/esm/vs/editor/editor.api";
import "monaco-editor/esm/vs/basic-languages/java/java.contribution";
import "monaco-editor/esm/vs/basic-languages/python/python.contribution";
import "monaco-editor/esm/vs/basic-languages/cpp/cpp.contribution";
import EditorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import { useApp } from "../context";
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
  const dark =
    theme === "dark" ||
    (theme === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
  useEffect(() => {
    monaco.editor.defineTheme("1on1-light", {
      base: "vs",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#ffffff",
        "editorLineNumber.foreground": "#a3abba",
        "editor.lineHighlightBackground": "#f3f5fa",
      },
    });
  }, []);
  return (
    <Editor
      height="440px"
      language={language === "cpp" ? "cpp" : language}
      value={value}
      onChange={(v) => onChange(v ?? "")}
      theme={dark ? "vs-dark" : "1on1-light"}
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
