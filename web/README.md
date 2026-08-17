# Stage V browser runtime CI candidate

This directory contains the browser-runtime parity harness for Empirical Finance Lab v0.1. It is **not** a second econometric implementation. Scientific calculations remain in `src/empirical_finance_lab/` and run through pinned Pyodide inside a module Web Worker.

## Environment separation

- `tsconfig.json`: browser/Web Worker source; Node globals are not exposed.
- `tsconfig.node.json`: Playwright/Vite/tooling tests with explicit Node types.
- `vitest.config.ts`: unit tests only under `src/**/*.test.ts`.
- `playwright.config.ts`: real-browser tests under `tests/**/*.spec.ts`.

## Generated scientific assets

`efl-core.json`, `stage5-parity-cases.json`, and `stage5-runtime-pin.json` are generated derivatives. They are created once in Stage V preflight under the frozen Stage IV Python environment and transferred to each browser job as one workflow artifact. They are intentionally ignored by Git and must not be edited manually.

For local static preparation, run from repository root:

```bash
python tools/check_stage5_static_gate.py
```

The `npm run build` command is deliberately a **pure Vite build** and never regenerates scientific references.

Stage V is accepted only after one Git commit passes preflight plus Chromium, Firefox, and WebKit parity/privacy jobs.
