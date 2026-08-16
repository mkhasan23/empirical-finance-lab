# Changelog

## 0.0.0 - Stage V browser-runtime CI candidate (2026-08-16)

- Added a pinned Pyodide module Web Worker around the authoritative Stage IV Python core; no second econometric implementation was created.
- Added strict browser-vs-Node TypeScript boundaries and explicit Vitest-vs-Playwright test discovery boundaries.
- Added SHA-256 source-bundle verification, same-origin core enforcement, row/permutation guards, cancellation, stale-result rejection, worker-error propagation, a 45-second scientific watchdog, and a 120-second progress-aware initialization stall watchdog.
- Added representative CPython-to-Pyodide parity, zero-analysis-network privacy checks, and isolated Chromium/Firefox/WebKit CI jobs.
- Stage V scientific browser assets are generated once in preflight under the frozen Stage IV Python environment and transferred unchanged to all browser jobs using GitHub Actions artifacts. Browser jobs perform pure Vite builds and do not regenerate CPython reference outcomes.
- Generated Stage V browser JSON payloads are derived artifacts and are not committed as source authority.
- Stage III validation fixtures and the Stage IV Python numerical core remain unchanged.
- Status remains **CI candidate** until the same commit passes Stage III, Stage IV, Stage V preflight, Chromium, Firefox, and WebKit.

## 0.0.0 - Stage IV numerical core (2026-08-16)

- Implemented the authoritative Python event-study numerical core against the frozen Stage III corpus.
- Added explicit validation, event-time construction, market-model/market-adjusted AR/CAR, classical predictive CAR inference, seeded PCG64 permutation inference, historical placebo diagnostics, robustness, deterministic audit/Referee Mode, and reproducibility identifiers.
- Added Stage IV operational clarifications for non-destructive extreme-return warnings, historical placebo timing, assumption diagnostics, and deterministic hashing.
- Added complete Stage III-fixture tests plus invariance, runtime-risk, reproducibility, and end-to-end tests.
- Added a separate Stage IV numerical-core CI workflow.
- No Stage III golden/reference answer was changed.

## 0.0.0 - Stage III (2026-08-16)

- Created GitHub-ready repository skeleton.
- Added authoritative validation corpus and reference-output manifest.
- Added schemas, citation metadata, license, scientific change governance, and corpus-integrity CI.
- No production econometric implementation existed at this stage.
