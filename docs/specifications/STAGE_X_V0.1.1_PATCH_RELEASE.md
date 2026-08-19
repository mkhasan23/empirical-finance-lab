# Stage X — v0.1.1 Patch Release Interoperability Hardening

## Purpose

Stage X governs the v0.1.1 patch release. The patch improves browser/source-data interoperability, preprocessing provenance, citation, public discoverability, and release-version consistency without changing the accepted econometric implementation.

## Scientific authority

The scientific/external-validation authority remains:

- Stage VIII baseline: `a694d49df9716f9f87d359385598237363e4c3fc`
- Stage VIII tree: `621b0cafdcad3711d2aba3bef698d2e78d022144`

The immutable historical v0.1.0 release remains fixed at:

- tag: `v0.1.0`
- commit: `faf3dc6c5702dad3f5abd1dd15f7697fab5a5831`

Stage X does not regenerate golden answers and does not redefine Stage VIII real-data evidence.

## Patch scope

v0.1.1 permits the following non-econometric changes:

1. deterministic browser intake support for `YYYY-MM-DD`, `YYYY/MM/DD`, and `YYYYMMDD`;
2. explicit researcher selection for ambiguous `MM/DD/YYYY` versus `DD/MM/YYYY`;
3. canonicalization to strict `YYYY-MM-DD` before duplicate/order/effective-date checks;
4. locked date-parser and source-row provenance;
5. visible CRSP-shaped mapping suggestions for `DlyCalDt`, `DlyRet`, and `vwretd`;
6. visible author/citation information and release citation derived from authoritative software version;
7. canonical/Open Graph/search verification metadata and sitemap support;
8. documentation and release-governance corrections.

The general browser estimation-window default remains `[-250,-30]` and researcher-editable. The Stage VIII validation design `[-256,-46]` remains evidence-specific.

## Forbidden scientific changes

Stage X must not change:

- market-model estimation;
- market-adjusted computation;
- abnormal returns or CAR;
- classical predictive CAR inference;
- PCG64 permutation inference;
- historical placebo computation;
- robustness computation;
- Stage III golden/reference outputs;
- Stage VIII locked numerical evidence.

Inside `src/empirical_finance_lab/**`, only the exact audited `__init__.py` version-metadata state may differ from the frozen scientific tree.

## Date-interoperability contract

Auto detection may accept only intrinsically unambiguous year-first formats. EFL must never guess the meaning of an ambiguous year-last slash date.

Canonicalization must occur before:

- duplicate detection;
- ordering checks;
- effective-trading-date suggestion.

The raw local-file SHA-256 remains the hash of the original bytes. The engine-input SHA-256 remains the hash of the canonical normalized CSV. The locked specification and reproducibility bundle record the date interpretation and transformation provenance.

## Release contract

The v0.1.1 release requires:

1. Stages III–VIII green on the exact candidate;
2. historical Stage IX v0.1.0 integrity green;
3. Stage X gate green on the exact candidate;
4. governed pull-request integration to `main`;
5. fresh Stage III–X exact-main validation;
6. immutable `v0.1.1` tag at that exact main commit;
7. tag-triggered Stage X proof that tag version equals software version and tag target equals exact current `origin/main`;
8. GitHub Release published from the already-validated tag.

The v0.1.0 tag is never moved or recreated.

## DOI boundary

No DOI is claimed unless an archival service actually issues one. A later DOI must identify the exact immutable v0.1.1 release. Placeholder or guessed identifiers are forbidden.
