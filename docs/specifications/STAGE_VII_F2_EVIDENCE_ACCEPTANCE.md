# Stage VII-F2 — Formal Evidence and Acceptance Contract

## Purpose

F2 converts Stage VII's accumulated release-hardening proof into an auditable acceptance record without changing the scientific core, browser analysis logic, dependency graph, runtime pins, watchdogs, or identifier definitions.

## Self-reference rule

A committed file cannot truthfully contain the SHA of the commit that will contain that file before the commit exists. F2 therefore forbids treating a guessed or precomputed future SHA as evidence.

The committed human-readable report records the exact **validated predecessor**. The Stage VII CI workflow then generates a machine-readable acceptance artifact after checkout of the real candidate commit, using `${{ github.sha }}` / `EFL_BUILD_COMMIT` as the candidate identity.

## Human-readable evidence

F2 requires:

- `docs/STAGE_VII_EVIDENCE_REPORT.md`; and
- `docs/STAGE_VII_ACCEPTANCE_CHECKLIST.md`.

The report must contain the exact predecessor workflow ledger, artifact digests, deployment URL, toolchain/browser evidence, security/privacy/reproducibility/accessibility evidence, known limitations, and the WebKit rerun disclosure.

The checklist must separate established branch evidence from F2 post-commit evidence and post-integration `main` gates.

## Machine-readable evidence

The final Stage VII `evidence` job must depend on successful `build`, `deploy`, and `verify-live` jobs. It must not declare acceptance if one of those jobs fails or is skipped.

The writer `tools/write_stage7_f2_ci_evidence.py` emits schema:

`efl-stage7-acceptance-evidence-1`

The generated JSON must record:

- exact repository;
- exact commit SHA;
- exact Git ref;
- workflow name, run ID, and run attempt;
- Pages URL;
- upstream Stage VII job results;
- production manifest schema, file count, total bytes, and tree SHA-256;
- exact evidence-job Python, Node, and npm versions;
- scientific dependency pins;
- locked frontend tool versions;
- locked Playwright Chromium/Firefox/WebKit browser versions and revisions;
- SHA-256 hashes of critical repository authority files;
- all external GitHub Actions full-SHA pins; and
- the explicit release-state boundary.

The workflow uploads this JSON as artifact:

`stage7-acceptance-evidence`

with 30-day retention.

## Acceptance semantics

Passing F2 on the feature branch means only:

**Stage VII branch candidate ready for governed integration.**

It does not mean:

- Stage VII accepted on `main`;
- Public Beta;
- formal `v0.1.0`;
- DOI release; or
- formal WCAG certification.

Stage VII acceptance requires integration to `main` followed by a successful exact-main-commit III–VII gate.

## Frozen exclusions

F2 must not modify:

- `src/empirical_finance_lab/**`;
- `validation/**` scientific fixtures;
- `web/src/**` application/scientific behavior;
- `web/package.json` or `web/package-lock.json`;
- runtime pins;
- browser watchdogs/timeouts;
- AnalysisID or ExecutionID definitions.
