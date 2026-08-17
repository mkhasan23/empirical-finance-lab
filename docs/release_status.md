# Empirical Finance Lab release status

## Current state

Empirical Finance Lab is currently a **Stage VII release-hardening candidate**.

- Stages III–VI form the accepted scientific/runtime/application baseline.
- Stage VII candidate work has validated GitHub Pages deployment, document security/privacy controls, supply-chain governance, build provenance, reproducibility round-trip, synthetic onboarding, and automated accessibility/responsive behavior on the feature branch.
- Stage VII as a whole is **not yet accepted**.
- The project is **not Public Beta**.
- There is **no formal `v0.1.0` release**.
- There is **no version-specific DOI**.
- `CITATION.cff` therefore remains at `0.0.0`.

The publicly reachable GitHub Pages site is a candidate deployment used for release-hardening verification:

`https://mkhasan23.github.io/empirical-finance-lab/`

Public reachability does not change the release state.

## What remains before Stage VII acceptance

Stage VII still requires:

1. this release-documentation/metadata contract to pass its exact-commit gate;
2. the formal Stage VII evidence report and acceptance checklist;
3. a complete feature-branch III–VII gate;
4. governed integration to `main`; and
5. the required III–VII rerun on `main`.

Repository-level security settings that are intentionally deferred until the pinned workflows are on `main` are handled after that integration step.

## What comes after Stage VII

- **Stage VIII:** modest Public Beta / external validation.
- **Stage IX:** formal `v0.1.0` release and archival/DOI work when actually completed.

No Stage VII document should describe either later milestone as already achieved.

## Scientific and privacy boundary

The scientific authority remains the frozen Python core and authoritative validation corpus. Stage VII does not add econometric methods.

Research CSV data are opened locally in browser memory; EFL provides no research-data upload endpoint. The deployed candidate is tested for zero analysis-time network requests, exact build provenance, and privacy-preserving reproducibility behavior.

## First run

Use the deterministic synthetic tutorial in [`quickstart.md`](quickstart.md). It is a workflow/known-answer demonstration, not a real security, investment recommendation, or causal claim.

## Release and citation policy

See [`governance/release_policy.md`](governance/release_policy.md) for promotion gates and [`../CITATION.cff`](../CITATION.cff) for current pre-release citation metadata.
