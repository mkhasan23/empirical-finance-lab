# Empirical Finance Lab release status

## Current state

Empirical Finance Lab has an **accepted Stage VII release-hardening baseline on `main`** and an **accepted Stage VIII real-data external-validation baseline on `main`**.

- Accepted Stage VII baseline: `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.
- Accepted Stage VIII external-validation baseline: `a694d49df9716f9f87d359385598237363e4c3fc`.
- Accepted Stage VIII repository tree: `621b0cafdcad3711d2aba3bef698d2e78d022144`.
- Stages III–VI remain the accepted scientific/runtime/application foundation preserved by Stage VII.
- Stage VII release hardening remains **accepted** after governed integration and fresh Stage III–VII validation on the resulting `main` commit.
- Stage VIII real-data external validation is **accepted** after governed integration and fresh Stage III–VIII validation on exact `main` commit `a694d49df9716f9f87d359385598237363e4c3fc`.
- The project is **not Public Beta**.
- There is **no formal `v0.1.0` release**.
- There is **no version-specific DOI**.
- `CITATION.cff` therefore remains at `0.0.0`.

The publicly reachable GitHub Pages site is the validated Stage VII pre-release deployment:

`https://mkhasan23.github.io/empirical-finance-lab/`

Public reachability, Stage VII acceptance, and Stage VIII external-validation acceptance do not by themselves constitute Public Beta or a formal scholarly release.

## Stage VII formal evidence

The Stage VII branch evidence is consolidated in:

- [`STAGE_VII_EVIDENCE_REPORT.md`](STAGE_VII_EVIDENCE_REPORT.md); and
- [`STAGE_VII_ACCEPTANCE_CHECKLIST.md`](STAGE_VII_ACCEPTANCE_CHECKLIST.md).

The exact F2 branch candidate was `7236cb37a971edceed99981dd7d17e631868ee2b`. Its Stage VII workflow run `32073099350` completed successfully on attempt 2 and emitted `stage7-acceptance-evidence` artifact `9303611739` with digest `sha256:18df6b9b058de4d16d91d6c070996bb3356ba8f578440bb7f4b5365ea4978b5d`.

The accepted integration baseline is `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`. Fresh Stage III–VII workflows were then run on that `main` state; Stage V required a same-commit rerun and subsequently passed. Stage VII deployment/live verification also passed on `main`.

## Stage VIII real-data external-validation evidence

The Stage VIII scientific and licensing-boundary record is consolidated in [`STAGE_VIII_REAL_DATA_VALIDATION.md`](STAGE_VIII_REAL_DATA_VALIDATION.md).

The governed Stage VIII branch head was `6122a2b5ff0aaada0acb042b5d8f1d73621d7beb`. Pull request #10 was squash-integrated to exact `main` commit `a694d49df9716f9f87d359385598237363e4c3fc`, with repository tree `621b0cafdcad3711d2aba3bef698d2e78d022144`. The validated branch tree, PR merge-candidate tree, and resulting squash-merged main tree were identical.

Fresh main-push workflows then passed for:

- Stage III corpus integrity #68;
- Stage IV numerical core #66;
- Stage V browser runtime parity #63;
- Stage VI application UI #53;
- Stage VII release hardening #44; and
- Stage VIII real-data evidence #5.

Stage VI run `32210822522` initially encountered a WebKit cold-start/runtime stall. Only the failed jobs were rerun on the same exact main commit; attempt 2 passed preflight, Chromium, Firefox, WebKit, and `stage6-required`. No application, scientific-core, runtime-pin, watchdog, or validation-data code change was made in response.

The accepted Stage VIII external-validation baseline therefore remains `a694d49df9716f9f87d359385598237363e4c3fc`. A later reporting-only acceptance-record commit does not redefine that scientific/runtime/evidence baseline.

## Repository-governance completion

After the Stage VII post-merge main gate passed:

1. the temporary `stage-vii-release-hardening` deployment allowance was removed from the `github-pages` environment; and
2. repository-wide GitHub Actions full-length SHA enforcement was enabled.

These two repository settings are **repository administrator-confirmed**. They are not machine-read by the Stage VII source-tree gate because the workflow does not have repository-administration API authority.

After Stage VIII acceptance, merged temporary Stage VII/Stage VIII feature branches may be deleted locally and remotely without changing the accepted `main` history.

## Acceptance boundaries

### Stage VII

Stage VII is accepted as a **pre-release release-hardening milestone**. It does not alter the scientific scope and does not add econometric methods.

The accepted Stage VII baseline remains `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.

### Stage VIII real-data external validation

Stage VIII validates numerical implementation and cross-implementation parity on five heterogeneous authorized CRSP cases under one frozen design. The raw CRSP extract and five derived EFL input CSVs are not distributed with the repository.

This evidence does not establish causal identification, representativeness of the five events, or universal empirical validity. It also does not by itself declare Public Beta.

## What comes next

- **Public Beta promotion / external issue discovery:** deliberate promotion after the accepted Stage VIII real-data validation evidence, while retaining the pre-release noindex/citation/DOI boundary until that promotion is explicitly governed.
- **Stage IX:** formal `v0.1.0` release and archival/DOI work when actually completed.

Neither Public Beta nor Stage IX is currently achieved.

## Scientific and privacy boundary

The scientific authority remains the frozen Python core and authoritative validation corpus. Research CSV data are opened locally in browser memory; EFL provides no research-data upload endpoint. The deployed application is tested for zero analysis-time network requests, exact build provenance, and privacy-preserving reproducibility behavior.

Stage VIII adds public-safe real-data parity evidence while retaining the licensing boundary: observation-level CRSP data remain private.

## First run

Use the deterministic synthetic tutorial in [`quickstart.md`](quickstart.md). It is a workflow/known-answer demonstration, not a real security, investment recommendation, or causal claim.

## Release and citation policy

See [`governance/release_policy.md`](governance/release_policy.md) for promotion gates and [`../CITATION.cff`](../CITATION.cff) for current pre-release citation metadata.
