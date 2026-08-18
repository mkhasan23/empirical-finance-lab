# Release policy

Empirical Finance Lab uses exact-commit release gates because research-software credibility depends on the scientific implementation, runtime, deployment artifact, and documentation referring to the same tested state.

## Release states

### Development / pre-release (`0.0.0`)

Unreleased development work uses version `0.0.0`. Validated pre-release deployments may exist, but they are not scholarly releases and must not be presented as having a version-specific DOI.

### Stage VII — accepted release hardening

Stage VII hardens the accepted Stage III–VI scientific/application baseline. Feature-branch Stage VII deployments are candidate deployments; Stage VII acceptance occurs only after the governed main integration and required post-integration gates pass.

Stage VII acceptance requires:

- authoritative Stage III fixtures remain intact;
- Stage IV numerical-core tests remain green;
- Stage V browser-runtime parity remains green;
- Stage VI application gates remain green;
- Stage VII security, supply-chain, provenance, reproducibility, onboarding, accessibility/responsive, documentation, and final evidence contracts are green on the exact candidate commit;
- the governed integration reaches `main`;
- the required main-branch III–VII gates pass after integration;
- temporary feature-branch deployment permission is removed; and
- repository-wide full-action-SHA enforcement is enabled after pinned workflows are validated on `main`.

The current accepted Stage VII baseline is recorded in `docs/release_status.md`; this policy deliberately keeps the acceptance rule separate from a mutable current-status SHA.

A public research release is blocked if any authoritative scientific fixture fails, any critical audit condition can leak a stale/partial result, cross-runtime parity is not established, the tested production artifact differs from the deployed artifact, privacy/security/reproducibility gates fail, or a numerical change lacks disclosed impact classification.

### Stage VIII — Public Beta / external validation

Public Beta is a separate milestone after Stage VII acceptance. It is intended for modest external validation and issue discovery. Public Beta status must not be inferred merely because GitHub Pages is publicly reachable or because Stage VII has been accepted.

### Stage IX — formal `v0.1.0` release

The formal `v0.1.0` release requires the validated release candidate to be tagged from the governed default-branch state, accompanied by consistent changelog/citation/release metadata and the project’s formal archival/DOI step when that step is actually completed.

## Scientific-change rule

Golden/reference results are independent authority. They must not be regenerated merely because production code disagrees with them. Numerical or methodology changes require the classifications and evidence described in `CONTRIBUTING.md`.

## Dependency and supply-chain rule

Dependency changes follow `docs/governance/DEPENDENCY_UPDATE_POLICY.md`. Scientific Python/runtime changes are deliberate scientific-maintenance events, not ordinary automated dependency refreshes.

## Citation rule

`CITATION.cff` remains at `0.0.0` during pre-release development. Pre-release deployments have no version-specific DOI. Researchers should cite the exact formal release they actually use once such a release exists.
