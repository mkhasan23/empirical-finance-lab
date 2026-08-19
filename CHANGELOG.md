# Changelog

## 0.0.0 - Stage VIII real-data external validation accepted (2026-08-18)

- Added a public-safe Stage VIII real-data validation evidence layer anchored to authorized local CRSP source data without committing observation-level CRSP data or the five derived EFL input CSVs.
- Independently recomputed five heterogeneous event-study cases under one prespecified market-model design and matched the frozen EFL scientific core at essentially machine precision; every permutation extreme count matched exactly.
- Preserved the Stage III validation corpus and Stage IV numerical authority; Stage VIII did not change the scientific core.
- Added a closed Stage VIII evidence subtree and CI gate that validates the five locked specifications, hashes, analysis IDs, parity summaries, exact permutation counts, and CRSP licensing/privacy boundary.
- Integrated the validated Stage VIII branch through pull request #10 to exact main baseline `a694d49df9716f9f87d359385598237363e4c3fc` with repository tree `621b0cafdcad3711d2aba3bef698d2e78d022144`.
- Fresh Stage III–VIII main-push workflows passed on that baseline. Stage VI's first main attempt encountered a transient WebKit cold-start/runtime stall; rerunning only the failed jobs on the same commit passed without any source change.
- Stage VIII external-validation acceptance remains **pre-release**: EFL is **not Public Beta**, there is no formal `v0.1.0` release, and there is no version-specific DOI.

## 0.0.0 - Stage VII release hardening accepted (2026-08-17)

- Added a committed frontend lockfile and converted controlled CI installation to `npm ci`.
- Added exact tested-artifact GitHub Pages deployment plus post-deployment byte-for-byte and live runtime verification.
- Added an enforcing document CSP/referrer boundary, explicit browser privacy/network checks, and a documented worker/network security boundary.
- Added full-SHA GitHub Actions governance, scoped Dependabot configuration, and dependency-update policy without placing the scientific Python authority on automatic version updates.
- Added deterministic build provenance tied to the exact Git commit and propagated the build commit/mode/source through the browser runtime, Python environment, and reproducibility export.
- Added strict privacy-preserving reproducibility ZIP round-trip contract: verify the exact original local CSV externally, reconstruct normalized engine input, rerun the authoritative browser core, compare identities/scientific results, and require deterministic byte-identical re-export.
- Added a deterministic 180-row synthetic onboarding dataset and quickstart tied to the frozen KA-003 AR/CAR known answer.
- Added automated accessibility/keyboard/responsive contracts, including native `hidden` semantics and completed-result containment at 320/390/768/1280 px.
- Added formal Stage VII branch evidence and exact-commit acceptance evidence, followed by governed squash integration to `main` and fresh Stage III–VII main-branch validation.
- Accepted Stage VII at baseline `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`; the same-commit Stage V post-merge gate required a rerun and then passed. The temporary feature-branch Pages allowance was removed and repository-wide full-action-SHA enforcement was enabled by the repository administrator.
- Stage VII acceptance remains **pre-release**: this is **not Public Beta**, not a formal `v0.1.0` release, and has no version-specific DOI.

## 0.0.0 - Stage VI research application UI (2026-08-16)

- Added the researcher-facing audit-first event-study workflow: local file intake, explicit column mapping/units, event-date confirmation, prespecification, specification locking, analysis, audit, robustness, placebo, Referee Mode, and reproducibility export.
- Added deterministic local CSV normalization with explicit sort approval and normalized-to-original source-row provenance; original local-file SHA-256 and normalized engine-input SHA-256 are exported separately.
- Added a deterministic dependency-free ZIP reproducibility bundle without automatically including proprietary raw input data.
- Added responsive, keyboard-addressable, status-message-aware UI semantics and exact-value table alternatives for charts.
- Added Stage VI unit tests and Chromium/Firefox/WebKit end-to-end researcher-journey CI.
- Added a frozen SHA-256 scientific-tree manifest protecting the Stage III validation corpus and Stage IV Python core from interface drift.
- Stage VI is part of the accepted scientific/application baseline preserved by Stage VII release hardening.

## 0.0.0 - Stage V browser runtime (2026-08-16)

- Added a pinned Pyodide module Web Worker around the authoritative Stage IV Python core; no second econometric implementation was created.
- Added strict browser-vs-Node TypeScript boundaries and explicit Vitest-vs-Playwright test discovery boundaries.
- Added SHA-256 source-bundle verification, same-origin core enforcement, row/permutation guards, cancellation, stale-result rejection, worker-error propagation, a 45-second scientific watchdog, and a 120-second progress-aware initialization stall watchdog.
- Added representative CPython-to-Pyodide parity, zero-analysis-network privacy checks, and isolated Chromium/Firefox/WebKit CI jobs.
- Stage V scientific browser assets are generated once in preflight under the frozen Stage IV Python environment and transferred unchanged to all browser jobs using GitHub Actions artifacts. Browser jobs perform pure Vite builds and do not regenerate CPython reference outcomes.
- Generated Stage V browser JSON payloads are derived artifacts and are not committed as source authority.
- Stage III validation fixtures and the Stage IV Python numerical core remain unchanged.

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
