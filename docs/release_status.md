# Empirical Finance Lab release status

## Current state

Empirical Finance Lab is configured for the **v0.1.1 validated patch release line**.

- Accepted Stage VII release-hardening baseline: `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.
- Accepted Stage VIII scientific/external-validation baseline: `a694d49df9716f9f87d359385598237363e4c3fc`.
- Accepted Stage VIII scientific repository tree: `621b0cafdcad3711d2aba3bef698d2e78d022144`.
- Immutable historical v0.1.0 release tag: `v0.1.0`, fixed at `faf3dc6c5702dad3f5abd1dd15f7697fab5a5831`.
- Intended patch release tag: `v0.1.1`; this tag is now issued and validated at `55bc447141dde59853e670687bf46e383679eb78`.
- Formal v0.1.1 patch-release authority: immutable tag `v0.1.1` at `55bc447141dde59853e670687bf46e383679eb78`.
- No version-specific DOI is claimed unless an archival DOI is actually minted and recorded; that condition is now satisfied for v0.1.1 with version DOI `10.5281/zenodo.22018410`. The all-versions Concept DOI is `10.5281/zenodo.22018409`.

The public GitHub Pages application is:

`https://mkhasan23.github.io/empirical-finance-lab/`

Research CSVs are opened locally in browser memory. EFL provides no research-data upload endpoint, and scientific analysis-phase network traffic is required to remain zero.

## v0.1.1 patch scope

v0.1.1 is an interoperability/usability/citation/discoverability patch, not a numerical-method change.

The browser now accepts deterministic year-first source dates (`YYYY-MM-DD`, `YYYY/MM/DD`, `YYYYMMDD`) and requires an explicit researcher choice for ambiguous year-last slash dates (`MM/DD/YYYY` versus `DD/MM/YYYY`). Accepted dates are canonicalized to `YYYY-MM-DD` before duplicate, ordering, and effective-trading-date checks. The locked specification and reproducibility bundle retain date-parser provenance, and original-file versus engine-input SHA-256 identities remain separate.

CRSP-shaped headers `DlyCalDt`, `DlyRet`, and `vwretd` receive visible mapping suggestions. The application also exposes author/citation metadata and public search-discovery metadata.

The general browser estimation-window default remains `[-250,-30]` and is researcher-editable. The accepted Stage VIII real-CRSP validation design remains `[-256,-46]`; v0.1.1 does not redefine that evidence.

## Scientific validation authority

The formal patch release does not redefine the independent scientific authority.

The accepted Stage III validation corpus and Stage IV numerical modules remain the scientific foundation. Stage VI byte-protection continues to preserve that corpus/core. For v0.1.1, every econometric module remains byte-identical to the accepted frozen tree. The only permitted current delta inside `src/empirical_finance_lab/**` is the exact `__init__.py` release-metadata transition to version `0.1.1`.

The accepted Stage VIII external-validation baseline remains:

`a694d49df9716f9f87d359385598237363e4c3fc`

with tree:

`621b0cafdcad3711d2aba3bef698d2e78d022144`

## Real-CRSP external validation

Stage VIII independently recomputed five heterogeneous real CRSP event-study cases outside the EFL production core under one frozen design and compared them with EFL.

Across the scientific comparison fields:

- maximum absolute numerical delta: `2.7755575615628914e-16`;
- all five cases satisfied the established numerical tolerances; and
- all five permutation extreme counts matched exactly.

Licensed CRSP observations and the five derived EFL input CSVs remain private and are not distributed. This is tested-case numerical parity, not CRSP/WRDS/vendor endorsement, universal validation, or causal certification.

## Stage VII evidence retained

The Stage VII release-engineering evidence remains consolidated in:

- [`STAGE_VII_EVIDENCE_REPORT.md`](STAGE_VII_EVIDENCE_REPORT.md); and
- [`STAGE_VII_ACCEPTANCE_CHECKLIST.md`](STAGE_VII_ACCEPTANCE_CHECKLIST.md).

The accepted Stage VII integration baseline remains `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`. Repository administrator-confirmed governance settings remain part of that historical acceptance record.

## Historical v0.1.0 authority

Formal release tag: `v0.1.0`. The immutable `v0.1.0` tag remains the first formal EFL release. Current Stage IX governance verifies that historical tag rather than forcing later patch lines to masquerade as v0.1.0. The tag itself is never moved, recreated, or redefined.

## Stage X patch-release contract

The v0.1.1 release requires all of the following:

1. Stages III–VIII pass on the exact candidate commit.
2. The historical Stage IX v0.1.0 integrity gate remains green.
3. `stage10-required` passes on that same candidate commit.
4. The candidate is integrated to `main` through the governed pull-request path.
5. Stages III–X pass again on the resulting exact `main` commit.
6. The immutable tag `v0.1.1` is created at that exact validated main commit.
7. The tag-triggered Stage X gate verifies `tag == software version` and `tag target == exact current origin/main commit`.
8. The GitHub Release is published from that already-validated tag.

The release tag must never be moved to a different commit.

## Citation and DOI boundary

`CITATION.cff` identifies version `0.1.1`, release date `2026-08-19`, and the exact Zenodo version DOI `10.5281/zenodo.22018410`. The formal patch-release citation authority is the validated immutable `v0.1.1` tag at `55bc447141dde59853e670687bf46e383679eb78`.

Zenodo archived the exact v0.1.1 GitHub release snapshot and assigned version DOI `10.5281/zenodo.22018410`. The Concept DOI `10.5281/zenodo.22018409` represents the EFL software collection across versions and resolves to the latest archived version. Exact-version reproducibility citations should use `10.5281/zenodo.22018410`.

EFL must never invent, guess, swap, or advertise an identifier that has not actually been issued and verified against the archival record.

## External feedback

Post-release issue discovery remains open through the structured **Researcher feedback** issue form. Public issues must not contain proprietary, licensed, confidential, or observation-level research data; minimal synthetic reproductions are preferred.

## First run

Use the deterministic synthetic tutorial in [`quickstart.md`](quickstart.md). Its `[-140,-20]` estimation window is a short synthetic known-answer tutorial specification, not the general browser default and not the Stage VIII real-CRSP validation design.

## Release policy

See [`governance/release_policy.md`](governance/release_policy.md) for the exact promotion, tag, scientific-change, dependency, and archival rules.
