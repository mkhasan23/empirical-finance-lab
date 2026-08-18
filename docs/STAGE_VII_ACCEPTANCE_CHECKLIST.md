# Stage VII Acceptance Checklist

This checklist records the completed Stage VII acceptance state. It must not be used to promote the project to Public Beta or `v0.1.0`.

Accepted Stage VII baseline: `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.

## A. Accepted scientific foundation

- [x] Stage III corpus integrity preserved.
- [x] Stage IV numerical core preserved.
- [x] Stage V browser scientific parity preserved.
- [x] Stage VI application workflow preserved.
- [x] Stage VII adds no econometric method and does not redefine AnalysisID or ExecutionID.

## B. Reproducible build and deployment

- [x] Frontend dependency graph is locked and CI uses `npm ci`.
- [x] Pages build targets `/empirical-finance-lab/`.
- [x] Production dist is manifest-hashed before browser smoke testing.
- [x] Production dist is re-verified after smoke testing.
- [x] Deployment consumes the tested artifact without rebuilding.
- [x] Live verification compares deployed HTTPS bytes with the tested manifest.

## C. Security, privacy, and supply chain

- [x] Enforcing CSP and `no-referrer` document policy are validated.
- [x] Local-production and live tests fail on document CSP violations.
- [x] Scientific analysis-phase network traffic is zero.
- [x] External Actions are pinned to full commit SHAs.
- [x] Dependabot update policy is scoped to npm development/test tooling and GitHub Actions.
- [x] Scientific Python dependency updates remain deliberate rather than automatic.

## D. Provenance and reproducibility

- [x] Production build is tied to the exact Git commit.
- [x] Browser and Python-core build provenance must agree.
- [x] Reproducibility ZIP round trip reconstructs and reruns the archived analysis.
- [x] Re-exported reproducibility ZIP must be byte-identical.

## E. Usability hardening

- [x] Deterministic synthetic tutorial and known-answer contract are validated.
- [x] Keyboard semantics are automatically validated.
- [x] Native hidden-state semantics are validated.
- [x] Completed-result layout is checked at 320 / 390 / 768 / 1280 px.
- [x] Accessibility language does not overclaim WCAG certification or manual assistive-technology testing.

## F. Release-state integrity

- [x] Public documentation records Stage VII as accepted on `main` while remaining pre-release.
- [x] Public documentation says not Public Beta.
- [x] No formal `v0.1.0` release is claimed.
- [x] No version-specific DOI is claimed.
- [x] `CITATION.cff` remains pre-release version `0.0.0`.
- [x] Pre-release site remains `noindex,nofollow`.

## G. Formal branch evidence

- [x] Fully validated F1 predecessor is recorded at `27ac2c64b3accc0af6bd26f7986fd5bf4ac21af5`.
- [x] F1 predecessor III–VII run IDs and Stage VII artifact digests are recorded in the formal evidence report.
- [x] Stage VI predecessor WebKit timeout/rerun history is disclosed rather than omitted.
- [x] Exact F2 commit `7236cb37a971edceed99981dd7d17e631868ee2b` passed Stages III–VII.
- [x] Exact F2 Stage VII run `32073099350` passed build, deployment, and live verification on attempt 2.
- [x] Exact F2 Stage VII run emitted `stage7-acceptance-evidence` artifact `9303611739` with digest `sha256:18df6b9b058de4d16d91d6c070996bb3356ba8f578440bb7f4b5365ea4978b5d`.

The committed F2 report remains the historical branch-candidate ledger. This checklist records the subsequent acceptance events without rewriting that historical evidence.

## H. Stage VII acceptance on `main`

- [x] Governed integration of the fully green Stage VII feature branch to `main`.
- [x] Stages III–VII reran successfully on accepted baseline `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`; Stage V required a same-commit rerun and then passed.
- [x] Temporary feature-branch deployment allowance was removed from the `github-pages` environment — repository administrator-confirmed.
- [x] Repository-wide GitHub Actions full-SHA enforcement was enabled after pinned workflows were validated on `main` — repository administrator-confirmed.

**Stage VII is accepted at baseline `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.** Stage VIII Public Beta remains a separate later decision.
