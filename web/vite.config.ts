import { defineConfig } from "vite";

export default defineConfig(({ mode }) => ({
  base: mode === "github-pages" ? "/empirical-finance-lab/" : "/",
  build: {
    target: "baseline-widely-available",
    sourcemap: true,
  },
}));
