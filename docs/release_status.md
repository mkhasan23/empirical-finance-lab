# Empirical Finance Lab release status

## Current state

Empirical Finance Lab is configured for the **v0.1.0 validated formal release line**.

- Accepted Stage VII release-hardening baseline: `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.
- Accepted Stage VIII scientific/external-validation baseline: `a694d49df9716f9f87d359385598237363e4c3fc`.
- Accepted Stage VIII scientific repository tree: `621b0cafdcad3711d2aba3bef698d2e78d022144`.
- Stage VIII acceptance-record main commit: `0d8dc18b751eb6bfda0b4285265d8a83bc816322`.
- Formal release tag: `v0.1.0`.
- Formal release authority: the exact commit named by `v0.1.0` **after** the tag-specific Stage IX gate passes.
- Before that tag exists and passes Stage IX, the governed `main` state carrying these metadata is the release candidate.
- No version-specific DOI is claimed unless an archival DOI is actually minted and recorded.

The public GitHub Pages application is:

`https://mkhasan23.github.io/empirical-finance-lab/`

The released application remains privacy-preserving: research CSVs are opened locally in browser memory, EFL provides no research-data upload endpoint, and scientific analysis-phase network traffic is required to remain zero.

## Scientific validation authority

The formal release does not redefine the independent scientific authority.

The accepted Stage III validation corpus and Stage IV numerical modules remain the scientific foundation. Stage VI byte-protection continues to preserve that corpus/core. For v0.1.0, the only permitted release-time change inside `src/empirical_finance_lab/**` is the exact `__init__.py` metadata transition from `0.0.0` to `0.1.0`; every econometric module remains byte-identical to the accepted frozen tree.

The accepted Stage VIII external-validation baseline remains:

`a694d49df9716f9f87d359385598237363e4c3fc`

with tree:

`621b0cafdcad3711d2aba3bef698d2e78d022144`

That baseline is intentionally retained even though the release metadata changes the software version and therefore runtime/reproducibility identifiers.

## Real-CRSP external validation

Stage VIII independently recomputed five heterogeneous real CRSP event-study cases outside the EFL production core under one frozen design and compared them with EFL.

Across the scientific comparison fields:

- maximum absolute numerical delta: `2.7755575615628914e-16`;
- all five cases satisfied the established numerical tolerances; and
- all five permutation extreme counts matched exactly.

The source CRSP extract and five derived EFL input CSVs remain private and are not distributed. The public repository contains only locked specifications, hashes, numerical summaries, and public-safe parity evidence.

This supports the statement **"validated on five real CRSP event-study cases."** It does not mean CRSP, WRDS, S&P, LSEG, or another vendor endorses EFL; it does not establish universal validity; and it does not establish causal identification.

## Stage VII evidence retained

The Stage VII release-engineering evidence remains consolidated in:

- [`STAGE_VII_EVIDENCE_REPORT.md`](STAGE_VII_EVIDENCE_REPORT.md); and
- [`STAGE_VII_ACCEPTANCE_CHECKLIST.md`](STAGE_VII_ACCEPTANCE_CHECKLIST.md).

The accepted Stage VII integration baseline remains `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`. Repository administrator-confirmed governance settings remain part of that historical acceptance record.

## Stage VIII evidence retained

The scientific and licensing-boundary record is:

[`STAGE_VIII_REAL_DATA_VALIDATION.md`](STAGE_VIII_REAL_DATA_VALIDATION.md)

Pull request #10 integrated the Stage VIII evidence to exact main baseline `a694d49df9716f9f87d359385598237363e4c3fc`. Fresh Stage III–VIII workflows passed on that state. The first Stage VI WebKit main attempt stalled during browser-runtime initialization; the same-commit failed-job rerun passed without source changes, so the event remains recorded as transient rather than a scientific/application correction.

## Stage IX formal-release contract

The v0.1.0 release is accepted only after all of the following hold on the governed release candidate:

1. Stages III–VIII pass on the exact candidate commit.
2. `stage9-required` passes on that same commit.
3. the candidate is integrated to `main` through the governed pull-request path;
4. Stages III–IX pass again on the resulting exact `main` commit;
5. the immutable tag `v0.1.0` is created at that exact validated `main` commit; and
6. the tag-triggered Stage IX gate verifies that the tag name and source version are identical.

The GitHub Release should then be published from that existing validated tag. The release must not be retagged to a different commit.

## Citation and DOI boundary

`CITATION.cff` identifies version `0.1.0` and the intended release date. The formal citation authority is the validated `v0.1.0` release.

A DOI is optional to the GitHub software release itself. If an archival service later mints a version-specific DOI, that DOI must refer to the exact `v0.1.0` release and may then be added to current citation/release metadata in a separately governed metadata-only update. EFL must never invent, reserve by guess, or advertise a DOI that has not actually been issued.

## External feedback

Post-release issue discovery remains open through the structured **Researcher feedback** issue form.

Public issues must not contain proprietary, licensed, confidential, or observation-level research data. Minimal synthetic reproductions are preferred.

## First run

Use the deterministic synthetic tutorial in [`quickstart.md`](quickstart.md). It is a workflow/known-answer demonstration, not a real security, investment recommendation, or causal claim.

## Release policy

See [`governance/release_policy.md`](governance/release_policy.md) for the exact promotion, tag, scientific-change, dependency, and archival rules.
