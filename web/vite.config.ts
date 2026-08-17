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

export default defineConfig(({ mode }) => ({
  base: mode === "github-pages" ? "/empirical-finance-lab/" : "/",
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
}));
