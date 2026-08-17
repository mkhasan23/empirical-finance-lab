# Empirical Finance Lab v0.1 — Stage V Browser Runtime Parity & Web Worker Integration

**Status:** CI CANDIDATE — NOT YET ACCEPTED

**Date:** 2026-08-16

## 1. Acceptance rule

Stage V is accepted only when the **same Git commit** passes all of the following:

- Stage III corpus integrity;
- Stage IV numerical core;
- Stage V preflight;
- Chromium Pyodide parity/privacy;
- Firefox Pyodide parity/privacy;
- WebKit Pyodide parity/privacy.

Local/static success alone is not Stage V acceptance.

## 2. Objective and authority

Stage V moves the already-validated Stage IV Python numerical core into the browser without creating a second econometric implementation.

`TypeScript harness -> module Web Worker -> pinned Pyodide -> authoritative EFL Python core`

Scientific authority remains `src/empirical_finance_lab/`. TypeScript is restricted to lifecycle, workload, transport, privacy, parity comparison, and presentation-boundary duties.

## 3. Runtime pins

The candidate pins Pyodide **314.0.4** and verifies the expected browser runtime as CPython **3.14.2**, NumPy **2.4.3**, and SciPy **1.18.0**. The browser scientific stack is deliberately allowed to differ from the frozen Stage IV CPython reference environment; that difference is tested through explicit parity rather than hidden by changing Stage IV.

Frontend candidate pins are TypeScript **5.9.3**, Vite **8.2.1**, Vitest **4.1.10**, Playwright **1.62.0**, and Node.js **24** in CI.

## 4. Authoritative asset model

`tools/build_stage5_browser_assets.py` packages the exact Stage IV Python source and representative CPython reference outcomes. Generated files are **derived CI/local artifacts**, not source authority, and are therefore ignored by Git:

- `web/public/efl-core.json`;
- `web/public/stage5-parity-cases.json`;
- `web/public/stage5-runtime-pin.json`.

The Stage V preflight job generates these files once under the frozen Stage IV scientific environment, statically validates them, and uploads them as one GitHub Actions artifact. Chromium, Firefox, and WebKit download that same artifact. Browser jobs MUST NOT regenerate CPython scientific references.

GitHub's artifact handoff is additionally digest-validated by the official artifact actions.

## 5. Browser/Node TypeScript boundary

Browser/Web Worker code and Node/tooling code use separate TypeScript configurations. Browser TypeScript does not expose Node globals. Playwright/Vite/tooling configuration uses explicit Node types.

Vitest owns only `src/**/*.test.ts`; Playwright owns `tests/**/*.spec.ts`.

## 6. Worker protocol and source integrity

Worker protocol version: **0.1.0**.

- `INIT` loads pinned Pyodide/scientific packages and installs the verified EFL source bundle.
- `RUN` calls only the authoritative Python `run_analysis` pathway.
- `PROGRESS` carries bounded initialization/execution phase information.
- `RESULT` carries the serialized Stage IV outcome associated with request/job IDs.
- `ERROR` carries the browser-boundary error envelope.

The worker rejects cross-origin EFL core bundles and verifies SHA-256 for the aggregate bundle and each Python source file. No user-supplied Python source is evaluated.

## 7. Runtime-risk controls

- browser input cap: **25,000 rows**;
- permutation count: **1,000–100,000**;
- scientific-computation watchdog: **45 seconds**;
- engine initialization: **120-second no-progress/stall watchdog**, refreshed only by valid initialization progress;
- worker cancellation destroys the active worker and forces clean reinitialization;
- concurrent analyses are rejected;
- stale/mismatched job results are rejected;
- worker `error`/`messageerror` propagate immediately;
- worker-destroying failures invalidate browser runtime state.

## 8. Initialization progress phases

The Web Worker exposes phases sufficient to identify cold-start stalls:

1. importing Pyodide module;
2. initializing Python runtime;
3. loading NumPy;
4. loading SciPy;
5. scientific runtime loaded;
6. fetching core bundle;
7. verifying core bundle;
8. installing core bundle;
9. core bundle installed;
10. importing EFL core.

A slow but advancing WebKit cold start is not terminated merely because total initialization exceeds two minutes; a phase with no valid progress for 120 seconds is terminated.

## 9. Cross-runtime parity

Representative CPython reference cases:

- `KA-003`;
- `INF-001`;
- `PLC-001`;
- `ROB-001`;
- `FM-001`.

Chromium executes the full set. Firefox and WebKit execute `KA-003`. Structural outputs require exact equality. Core continuous quantities use absolute tolerance `1e-12` and relative tolerance `1e-10`; p-values/tail proportions use absolute tolerance `1e-10`. Environment-specific execution metadata is excluded from scientific parity.

## 10. Privacy gate

There is no backend, telemetry, analytics, account system, or research-data upload endpoint. Initialization may request same-origin assets and the pinned `cdn.jsdelivr.net` Pyodide distribution. After initialization, the Playwright gate requires **zero network requests during scientific analysis**.

## 11. Browser CI architecture

Stage V uses a shared preflight followed by three isolated browser jobs:

`preflight -> {chromium, firefox, webkit}`

Preflight:

1. installs frozen Stage IV Python environment;
2. reruns Stage III and Stage IV gates;
3. generates and validates browser scientific assets once;
4. uploads the authoritative asset bundle using GitHub's official artifact action;
5. typechecks browser and Node/tooling environments;
6. runs Vitest;
7. builds the Vite harness.

Each isolated browser job:

1. checks out the same commit;
2. downloads the exact preflight-generated artifact;
3. installs pinned frontend dependencies;
4. performs a **pure Vite build** (no Python regeneration);
5. installs only its selected Playwright browser;
6. runs that browser's parity/privacy tests.

This prevents cumulative Pyodide/WebAssembly pressure and prevents browser-specific CPython reference regeneration.

## 12. Explicit nonclaims

Until the real GitHub workflow is green on all required jobs, Stage V is a **CI candidate**, not a completed stage. Even after Stage V passes, the project is not yet a polished public application, GitHub Pages release, DOI release, or multi-firm event-study platform.

## 13. Remaining release hardening

A committed npm lockfile remains required before public deployment/formal release. The current candidate pins direct frontend dependencies but intentionally does not claim full transitive-dependency reproducibility yet.
