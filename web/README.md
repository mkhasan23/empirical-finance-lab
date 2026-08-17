# Stage VI research application UI CI candidate

This directory contains the browser application for Empirical Finance Lab v0.1. Scientific calculations remain in `src/empirical_finance_lab/` and execute through the validated Stage V Pyodide module Web Worker.

## Environment separation

- `tsconfig.json`: browser/Web Worker source; Node globals are not exposed.
- `tsconfig.node.json`: Playwright/Vite/tooling tests with explicit Node types.
- `vitest.config.ts`: unit tests only under `src/**/*.test.ts`.
- `playwright.config.ts`: real-browser tests under `tests/**/*.spec.ts`.

## Application modules

- `application.ts`: researcher workflow orchestration and result-state lifecycle;
- `csvIntake.ts`: local CSV parsing, explicit mapping, intake checks, normalization/provenance;
- `specification.ts`: prespecification validation, event-date suggestion, locked spec construction;
- `resultsView.ts`: non-econometric rendering of core-returned values;
- `exportBundle.ts`: deterministic local reproducibility ZIP;
- `stage5Harness.ts`: preserves the validated Stage V parity API used by the Stage V release gate;
- `engineClient.ts` / `eflWorker.ts`: validated Stage V worker boundary.

## Data/privacy boundary

Research files are opened into browser memory. The Stage VI application does not persist them to localStorage/sessionStorage and does not transmit them to an EFL service. The original local-file SHA-256 is computed before mapping/normalization. The reproducibility archive records original and engine-input hashes separately and does not automatically include the proprietary source CSV.

## Generated scientific assets

`efl-core.json`, `stage5-parity-cases.json`, and `stage5-runtime-pin.json` are generated derivatives. CI creates them under the frozen Stage IV Python environment and transfers identical assets to each browser job. They are ignored by Git and must not be edited manually.

## Local checks

From repository root:

```bash
python tools/check_stage6_static_gate.py
```

From `web/` after installing the pinned development dependencies:

```bash
npm run typecheck
npm run test:unit
npm run build
npm run test:e2e:stage6
```

Stage VI is accepted only after one commit passes Stages III-V plus Stage VI preflight and Chromium/Firefox/WebKit end-to-end jobs.
