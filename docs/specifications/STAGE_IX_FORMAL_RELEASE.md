# Stage IX — Formal v0.1.0 release

## Purpose

Stage IX converts the fully validated Empirical Finance Lab v0.1 scientific/application stack into its first governed formal software release without changing the econometric implementation.

The release line is `0.1.0`; the immutable Git tag is `v0.1.0`.

## Scientific authority retained

Stage IX does **not** regenerate or redefine golden/reference results.

The scientific authority remains:

1. the frozen Stage III validation corpus;
2. the accepted Stage IV numerical implementation;
3. Stage V browser-runtime parity;
4. Stage VI researcher-facing application behavior;
5. Stage VII release/security/provenance/reproducibility controls; and
6. Stage VIII real-data external-validation evidence.

The accepted Stage VIII scientific/external-validation baseline is:

`a694d49df9716f9f87d359385598237363e4c3fc`

with scientific repository tree:

`621b0cafdcad3711d2aba3bef698d2e78d022144`

## Closed release-metadata exception inside the frozen core

The software version is imported by the authoritative Python core and therefore lives in `src/empirical_finance_lab/__init__.py`.

Stage IX permits exactly one frozen-tree transition:

- accepted pre-release `__init__.py` SHA-256:
  `ae3c71e4e8c916ed3cb2d6274be93b2770baf77953944b8e381dc8aa12c02765`
- exact v0.1.0 release-metadata `__init__.py` SHA-256:
  `b6fc4652ac03f40c1bbbfbcca0adf94544bc939a23cb1ac6f59b2edacb27a3fc`

Every other Stage IV Python module and every Stage III frozen validation file remains byte-identical to the accepted frozen scientific-tree manifest.

This exception is deliberately hash-closed. It is not a path-level permission to modify `__init__.py` arbitrarily.

Changing `__version__` changes runtime/reproducibility metadata and ExecutionID inputs. It does **not** change the scientific AR/CAR, inference, placebo, robustness, audit, or known-answer quantities.

## Release version authority

The scholarly software version is defined by:

- `pyproject.toml` project version;
- `src/empirical_finance_lab/__init__.py` runtime version; and
- `CITATION.cff` release version.

All three must equal `0.1.0`.

`web/package.json` remains a private frontend workspace package. Its internal `0.0.0` value is not the scholarly EFL software-version authority and is not exposed as the scientific runtime version.

## Real-data validation claim

The permitted public claim is:

> Validated on five real CRSP event-study cases. Independent recomputation outside the EFL production core matched EFL within machine precision, with identical permutation extreme counts across all five cases.

The maximum observed absolute comparison delta is:

`2.7755575615628914e-16`

This is a tested-case numerical-parity claim. It must not be presented as CRSP, WRDS, or vendor endorsement; universal validation; representativeness of the five events; or causal certification.

Licensed CRSP observations and private derived Stage VIII input CSVs remain outside the repository and release artifacts.

## Browser/reproducibility release state

The v0.1.0 production UI must:

- display the v0.1.0 validated-release state;
- report runtime `efl_version = 0.1.0`;
- be indexable (the former pre-release `noindex,nofollow` boundary is removed);
- retain the exact document CSP/referrer contract;
- retain zero scientific analysis-phase network requests;
- retain deterministic local reproducibility ZIP generation; and
- cite the exact release tag and build provenance without inventing a DOI.

## External feedback boundary

The repository includes a structured Researcher feedback form.

Public feedback must not contain proprietary, licensed, confidential, or observation-level research data. Minimal synthetic reproductions are preferred.

## DOI and archival boundary

A GitHub v0.1.0 release is valid without a DOI.

If an archival service later mints a version-specific DOI, it must identify the exact immutable `v0.1.0` release. The DOI may be added to current release/citation metadata only after it actually exists. No guessed, placeholder, or unissued DOI may be advertised.

A later DOI metadata update must not move or recreate the `v0.1.0` tag.

## Governed acceptance sequence

Stage IX is complete only after:

1. a dedicated release-candidate branch is based on the current governed `main`;
2. Stages III–VIII and `stage9-required` pass on the exact candidate commit;
3. a pull request to `main` passes the same required gates on GitHub's merge candidate;
4. the candidate is squash-integrated to `main`;
5. Stages III–VIII and `stage9-required` pass again on the exact resulting `main` commit;
6. the immutable tag `v0.1.0` is created at that exact validated main commit;
7. the tag-triggered Stage IX workflow passes and verifies `GITHUB_REF_NAME == v0.1.0`, source version `0.1.0`, and that the tagged commit is byte-for-byte the exact current `origin/main` commit; and
8. the GitHub Release is published from that already-validated tag.

No tag or GitHub Release is created before the exact-main gate in step 5 passes.

## Failure/adversarial expectations

The Stage IX gate must fail if:

- Python/package/citation versions disagree;
- the formal tag name disagrees with the software version or the tag target differs from the exact current `origin/main` commit;
- any Stage III frozen validation file changes;
- any Stage IV econometric module changes;
- `__init__.py` differs from the exact audited v0.1.0 metadata bytes;
- the Stage VIII public evidence gate fails or a known private CRSP artifact is committed;
- `REPOSITORY_MANIFEST.txt` differs from `git ls-files`;
- the release UI retains the pre-release noindex or Pre-alpha state;
- release browser tests expect a runtime version other than `0.1.0`;
- the public feedback form omits the proprietary-data prohibition; or
- the formal-release workflow uses mutable/unapproved GitHub Action references.
