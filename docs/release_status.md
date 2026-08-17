# Empirical Finance Lab release status

## Current state

Empirical Finance Lab is currently a **Stage VII release-hardening candidate**.

- Stages III–VI form the accepted scientific/runtime/application baseline.
- Stage VII candidate work has validated GitHub Pages deployment, document security/privacy controls, supply-chain governance, build provenance, reproducibility round-trip, synthetic onboarding, automated accessibility/responsive behavior, and release-documentation consistency on the feature branch.
- Stage VII as a whole is **not yet accepted**.
- The project is **not Public Beta**.
- There is **no formal `v0.1.0` release**.
- There is **no version-specific DOI**.
- `CITATION.cff` therefore remains at `0.0.0`.

The publicly reachable GitHub Pages site is a candidate deployment used for release-hardening verification:

`https://mkhasan23.github.io/empirical-finance-lab/`

Public reachability does not change the release state.

## Formal evidence

The Stage VII branch evidence is consolidated in:

- [`STAGE_VII_EVIDENCE_REPORT.md`](STAGE_VII_EVIDENCE_REPORT.md); and
- [`STAGE_VII_ACCEPTANCE_CHECKLIST.md`](STAGE_VII_ACCEPTANCE_CHECKLIST.md).

The committed report records the last fully validated predecessor. The F2 CI workflow then emits a machine-readable `stage7-acceptance-evidence` artifact for the exact commit under test, avoiding a self-referential hard-coded future SHA.

## What remains before Stage VII acceptance

Stage VII still requires:

1. the F2 evidence/acceptance contract to pass on its exact feature-branch commit, including III–VII and the exact-commit acceptance artifact;
2. governed integration to `main`;
3. the required III–VII rerun on the resulting exact `main` commit;
4. removal of the temporary feature-branch Pages deployment allowance; and
5. activation of repository-wide full-action-SHA enforcement after the pinned workflows are present and validated on `main`.

Repository-level security settings intentionally deferred until integration remain outside the branch source tree and are handled after the main-branch gate.

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
