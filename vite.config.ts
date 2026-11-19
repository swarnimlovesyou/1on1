import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8080" },
    // test runs write thousands of files under .cache; watching them (on OneDrive especially) crashes the watcher
    watch: { ignored: ["**/.cache/**", "**/backend/**", "**/docs/**", "**/scripts/**", "**/mcp/**", "**/test-results/**"] },
  },
  build: { chunkSizeWarningLimit: 800 },
});
