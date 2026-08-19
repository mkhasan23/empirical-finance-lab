# Empirical Finance Lab v0.1.1 browser application

This directory contains the browser application for the Empirical Finance Lab v0.1 workflow. The scholarly software-version authority is the validated Python core, which reports version `0.1.1` in runtime and reproducibility metadata.

The accepted Stage VII release-hardening baseline remains `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`. The accepted Stage VIII scientific/external-validation baseline remains `a694d49df9716f9f87d359385598237363e4c3fc`. The immutable historical `v0.1.0` tag remains fixed; the exact formal patch release becomes the immutable `v0.1.1` tag only after the Stage X exact-main/tag gates pass.

Scientific calculations remain in `src/empirical_finance_lab/` and execute through the validated Pyodide module Web Worker. The browser application does not create a second econometric implementation.

For the first-run tutorial, see [`../docs/quickstart.md`](../docs/quickstart.md). For the exact release boundary and acceptance record, see [`../docs/release_status.md`](../docs/release_status.md).

## v0.1.1 interoperability patch

The browser intake layer accepts deterministic year-first date formats `YYYY-MM-DD`, `YYYY/MM/DD`, and `YYYYMMDD`. Ambiguous `MM/DD/YYYY` versus `DD/MM/YYYY` values require an explicit researcher selection and are never guessed.

Accepted dates are canonicalized to strict `YYYY-MM-DD` before duplicate/order/effective-date checks. Date-parser provenance, original-file SHA-256, normalized engine-input SHA-256, and normalized-to-original source-row provenance remain auditable in the locked specification and reproducibility bundle.

CRSP-shaped headers `DlyCalDt`, `DlyRet`, and `vwretd` receive visible mapping suggestions. The general estimation-window default remains researcher-editable at `[-250,-30]`; the Stage VIII validated real-CRSP design `[-256,-46]` is not imposed as a universal default.

## Real-data validation

Five heterogeneous real CRSP event-study cases were independently recomputed outside the EFL production core and matched EFL within machine precision; the maximum absolute numerical delta was `2.7755575615628914e-16`, and all five permutation extreme counts matched exactly.

Licensed CRSP observations and private derived input CSVs are not distributed. This is tested-case numerical parity, not CRSP/WRDS/vendor endorsement or causal certification.

## Environment separation

- `tsconfig.json`: browser/Web Worker source; Node globals are not exposed.
- `tsconfig.node.json`: Playwright/Vite/tooling tests with explicit Node types.
- `vitest.config.ts`: unit tests only under `src/**/*.test.ts`.
- `playwright.config.ts`: accepted Stage V/VI real-browser tests.
- `playwright.stage7.config.ts`: production-subpath tests.
- `playwright.stage7.live.config.ts`: real deployed GitHub Pages verification.

## Application and release-hardening modules

- `application.ts`: researcher workflow orchestration and result-state lifecycle;
- `csvIntake.ts`: local CSV parsing, explicit mapping, intake checks, date canonicalization, and normalization/provenance;
- `specification.ts`: prespecification validation, event-date suggestion, locked spec construction;
- `resultsView.ts`: non-econometric rendering of core-returned values;
- `buildProvenance.ts`: deterministic build commit/mode/source authority;
- `exportBundle.ts`: deterministic local reproducibility ZIP with release citation derived from authoritative software version;
- `reproRoundTrip.ts` / `storedZip.ts`: strict bundle validation and privacy-preserving replay support;
- `stage5Harness.ts`: preserves the accepted browser-runtime parity API;
- `engineClient.ts` / `eflWorker.ts`: validated browser-to-Python worker boundary.

## Data/privacy boundary

Research files are opened into browser memory. The application does not persist them to localStorage/sessionStorage and does not transmit them to an EFL service. The original local-file SHA-256 is computed before mapping/normalization. The reproducibility archive records original and engine-input hashes separately and does not automatically include the proprietary source CSV.

Production validation verifies zero analysis-time network requests, exact deployed-artifact parity, document security policy, and the reproducibility ZIP round trip on the live HTTPS Pages deployment.

## Generated scientific assets

`efl-core.json`, `stage5-parity-cases.json`, and `stage5-runtime-pin.json` are generated derivatives. CI creates them under the frozen Python environment and transfers identical assets to browser jobs. They are ignored by Git and must not be edited manually.

## Local checks

From repository root:

```bash
python tools/check_stage6_static_gate.py
python tools/check_stage7_static_gate.py
python tools/check_stage7_d1_provenance_gate.py
python tools/check_stage7_e1_onboarding_gate.py
python tools/check_stage7_e2_accessibility_gate.py
python tools/check_stage7_f1_release_docs_gate.py
python tools/check_stage7_f2_evidence_gate.py
python tools/check_stage8_real_data_gate.py
python tools/check_stage9_release_gate.py
python tools/check_stage10_patch_release_gate.py
```

From `web/` after installing the locked development dependencies:

```bash
npm ci --no-audit --no-fund
npm run typecheck
npm run test:unit
npm run build:pages
npm run test:e2e:stage7
```

The live deployed-site suite is executed by the Stage VII workflow after deployment.

## Feedback

Use the repository's **Researcher feedback** issue form for workflow, documentation, browser/runtime, reproducibility, accessibility, or usability feedback. Do not attach proprietary, licensed, confidential, or observation-level research data to public issues.
