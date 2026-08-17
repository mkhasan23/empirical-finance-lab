# Stage VII release-hardening browser application

This directory contains the browser application for the Empirical Finance Lab v0.1 workflow. The repository is currently a **pre-release Stage VII release-hardening candidate**: it is not Public Beta and is not a formal `v0.1.0` release.

Scientific calculations remain in `src/empirical_finance_lab/` and execute through the validated Pyodide module Web Worker. Stage VII adds release/deployment, security, provenance, reproducibility, onboarding, and accessibility hardening without creating a second econometric implementation.

For the first-run tutorial, see [`../docs/quickstart.md`](../docs/quickstart.md). For the exact release boundary, see [`../docs/release_status.md`](../docs/release_status.md).

## Environment separation

- `tsconfig.json`: browser/Web Worker source; Node globals are not exposed.
- `tsconfig.node.json`: Playwright/Vite/tooling tests with explicit Node types.
- `vitest.config.ts`: unit tests only under `src/**/*.test.ts`.
- `playwright.config.ts`: accepted Stage V/VI real-browser tests.
- `playwright.stage7.config.ts`: production-subpath Stage VII candidate tests.
- `playwright.stage7.live.config.ts`: real deployed GitHub Pages verification.

## Application and release-hardening modules

- `application.ts`: researcher workflow orchestration and result-state lifecycle;
- `csvIntake.ts`: local CSV parsing, explicit mapping, intake checks, normalization/provenance;
- `specification.ts`: prespecification validation, event-date suggestion, locked spec construction;
- `resultsView.ts`: non-econometric rendering of core-returned values;
- `buildProvenance.ts`: deterministic build commit/mode/source authority;
- `exportBundle.ts`: deterministic local reproducibility ZIP;
- `reproRoundTrip.ts` / `storedZip.ts`: strict bundle validation and privacy-preserving replay support;
- `stage5Harness.ts`: preserves the accepted browser-runtime parity API;
- `engineClient.ts` / `eflWorker.ts`: validated browser-to-Python worker boundary.

## Data/privacy boundary

Research files are opened into browser memory. The application does not persist them to localStorage/sessionStorage and does not transmit them to an EFL service. The original local-file SHA-256 is computed before mapping/normalization. The reproducibility archive records original and engine-input hashes separately and does not automatically include the proprietary source CSV.

Stage VII additionally verifies zero analysis-time network requests, exact deployed-artifact parity, document security policy, and the reproducibility ZIP round trip on the live HTTPS Pages deployment.

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
```

From `web/` after installing the locked development dependencies:

```bash
npm ci --no-audit --no-fund
npm run typecheck
npm run test:unit
npm run build:pages
npm run test:e2e:stage7
```

The live deployed-site suite is executed by the Stage VII workflow after deployment and is not a substitute for the accepted Stage V/VI cross-browser gates.

Stage VII is accepted only after its complete feature-branch evidence/checklist is green, the governed integration reaches `main`, and the required main-branch gates pass. Until then, this directory documents a release-hardening candidate rather than a scholarly software release.
