import { defineConfig } from "vite";

export const DOCUMENT_CSP = [
  "default-src 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "script-src 'self'",
  "style-src 'self'",
  "img-src 'self' data:",
  "font-src 'self'",
  "connect-src 'self'",
  "worker-src 'self'",
  "frame-src 'none'",
  "media-src 'none'",
  "manifest-src 'self'",
  "form-action 'self'",
].join("; ");

function resolveBuildCommit(mode: string): string {
  const commit = (process.env.EFL_BUILD_COMMIT ?? "UNSET").trim();
  if (commit !== "UNSET" && !/^[0-9a-f]{40}$/.test(commit)) {
    throw new Error("EFL_BUILD_COMMIT must be UNSET or a lowercase 40-character Git commit SHA");
  }
  if (mode === "github-pages" && !/^[0-9a-f]{40}$/.test(commit)) {
    throw new Error("GitHub Pages candidates require EFL_BUILD_COMMIT to be the exact checked-out Git commit SHA");
  }
  return commit;
}

export default defineConfig(({ mode }) => {
  const buildCommit = resolveBuildCommit(mode);
  const buildMode = mode;
  const buildSource = process.env.GITHUB_ACTIONS === "true" ? "github-actions" : "local";

  return {
    base: mode === "github-pages" ? "/empirical-finance-lab/" : "/",
    define: {
      __EFL_BUILD_COMMIT__: JSON.stringify(buildCommit),
      __EFL_BUILD_MODE__: JSON.stringify(buildMode),
      __EFL_BUILD_SOURCE__: JSON.stringify(buildSource),
    },
    plugins: [
      {
        name: "efl-document-security-policy",
        transformIndexHtml() {
          return [
            {
              tag: "meta",
              attrs: {
                "http-equiv": "Content-Security-Policy",
                content: DOCUMENT_CSP,
              },
              injectTo: "head-prepend",
            },
            {
              tag: "meta",
              attrs: {
                name: "referrer",
                content: "no-referrer",
              },
              injectTo: "head-prepend",
            },
          ];
        },
      },
    ],
    build: {
      target: "baseline-widely-available",
      sourcemap: true,
    },
  };
});
