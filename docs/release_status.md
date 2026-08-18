# Empirical Finance Lab release status

## Current state

Empirical Finance Lab has an **accepted Stage VII release-hardening baseline on `main`**.

- Accepted Stage VII baseline: `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.
- Stages III–VI remain the accepted scientific/runtime/application foundation preserved by Stage VII.
- Stage VII release hardening is **accepted** after governed integration and fresh Stage III–VII validation on the resulting `main` commit.
- The project is **not Public Beta**.
- There is **no formal `v0.1.0` release**.
- There is **no version-specific DOI**.
- `CITATION.cff` therefore remains at `0.0.0`.

The publicly reachable GitHub Pages site is the validated Stage VII pre-release deployment:

`https://mkhasan23.github.io/empirical-finance-lab/`

Public reachability and Stage VII acceptance do not by themselves constitute Public Beta or a formal scholarly release.

## Formal evidence

The Stage VII branch evidence is consolidated in:

- [`STAGE_VII_EVIDENCE_REPORT.md`](STAGE_VII_EVIDENCE_REPORT.md); and
- [`STAGE_VII_ACCEPTANCE_CHECKLIST.md`](STAGE_VII_ACCEPTANCE_CHECKLIST.md).

The exact F2 branch candidate was `7236cb37a971edceed99981dd7d17e631868ee2b`. Its Stage VII workflow run `32073099350` completed successfully on attempt 2 and emitted `stage7-acceptance-evidence` artifact `9303611739` with digest `sha256:18df6b9b058de4d16d91d6c070996bb3356ba8f578440bb7f4b5365ea4978b5d`.

The accepted integration baseline is `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`. Fresh Stage III–VII workflows were then run on that `main` state; Stage V required a same-commit rerun and subsequently passed. Stage VII deployment/live verification also passed on `main`.

## Repository-governance completion

After the post-merge main gate passed:

1. the temporary `stage-vii-release-hardening` deployment allowance was removed from the `github-pages` environment; and
2. repository-wide GitHub Actions full-length SHA enforcement was enabled.

These two repository settings are **repository administrator-confirmed**. They are not machine-read by the Stage VII source-tree gate because the workflow does not have repository-administration API authority.

## Stage VII acceptance boundary

Stage VII is accepted as a **pre-release release-hardening milestone**. It does not alter the scientific scope and does not add econometric methods.

The accepted baseline remains `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`. A later reporting-only acceptance-record commit may have a different Git SHA; that does not redefine the accepted scientific/runtime/deployment baseline.

## What comes after Stage VII

- **Stage VIII:** modest Public Beta / external validation.
- **Stage IX:** formal `v0.1.0` release and archival/DOI work when actually completed.

Neither later milestone is currently achieved.

## Scientific and privacy boundary

The scientific authority remains the frozen Python core and authoritative validation corpus. Research CSV data are opened locally in browser memory; EFL provides no research-data upload endpoint. The deployed application is tested for zero analysis-time network requests, exact build provenance, and privacy-preserving reproducibility behavior.

## First run

Use the deterministic synthetic tutorial in [`quickstart.md`](quickstart.md). It is a workflow/known-answer demonstration, not a real security, investment recommendation, or causal claim.

## Release and citation policy

See [`governance/release_policy.md`](governance/release_policy.md) for promotion gates and [`../CITATION.cff`](../CITATION.cff) for current pre-release citation metadata.
