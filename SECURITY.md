# Security and Privacy

Empirical Finance Lab is pre-release research software. The Stage VII deployment candidate runs as a static browser application on GitHub Pages; the validated Python scientific core executes inside the browser through the pinned Pyodide runtime.

## Research-data privacy boundary

Research files are opened locally and held in browser memory. EFL provides no research-data upload service, analytics, telemetry, or remote crash reporting. The validated Stage VII production and live-site gates require zero network requests during scientific analysis.

Runtime initialization is intentionally narrower than general web access. The page loads the application and authoritative `efl-core.json` from the same-origin repository path. The scientific worker may obtain the pinned Pyodide runtime and its scientific packages from `cdn.jsdelivr.net` during initialization. The worker rejects an authoritative core-bundle URL whose origin differs from the deployed application origin and verifies the bundle and embedded source hashes before execution.

## Browser document security boundary

Production HTML is emitted with an enforcing **Content Security Policy** and **Referrer Policy** before resource-loading tags. The document policy restricts scripts, styles, connections, workers, forms, frames, objects, media, manifests, fonts, images, and base URLs to the minimum document-side surface required by EFL. It does not permit `unsafe-inline` or `unsafe-eval`, and the document itself is not granted access to `cdn.jsdelivr.net`.

The document policy permits only same-origin workers through `worker-src 'self'`. A normal dedicated worker has its own execution context, so EFL does not claim that the document CSP governs the worker's internal fetches. Worker-side initialization is instead bounded by version-controlled worker code, the same-origin authoritative-core check, pinned jsDelivr runtime URLs, hash verification, and the Stage VII production/live network audits.

The Referrer Policy is `no-referrer`.

## Supply-chain security boundary

All external GitHub Actions used by EFL workflows are pinned to a **full-length commit SHA** rather than mutable major-version tags. The approved SHAs are enforced by the Stage VII-C2 repository-wide supply-chain gate, and human-readable version annotations are retained beside each pin.

Dependabot is intentionally limited to weekly version-update proposals for frontend npm development tooling and GitHub Actions. Scientific Python is excluded from automatic version updates because numerical reproducibility and cross-runtime parity require deliberate validation before those versions move.

Repository administrators should enable the dependency graph, Dependabot alerts, and Dependabot security updates. After the SHA-pinned C2 workflows are merged to the default branch, the repository Actions setting that requires full-length SHA pins should also be enabled.

Dependency and action-update acceptance criteria are documented in `docs/governance/DEPENDENCY_UPDATE_POLICY.md`.

## Release posture

Stage VII remains a candidate-hardening stage, not Public Beta and not formal `v0.1.0`. `noindex,nofollow` remains in force until the later public-beta acceptance decision.

## Reporting a vulnerability

Please do not publish exploit details, sensitive data, or reproduction secrets in a public issue. Report security vulnerabilities privately to the maintainer so they can be evaluated before public disclosure.
