# Stage VII-F1 — Release Documentation and Metadata Contract

Status: implementation candidate on `stage-vii-release-hardening`.

## Purpose

F1 removes release-status drift accumulated while Stage VII technical controls were being implemented. It does not promote Empirical Finance Lab to Public Beta or `v0.1.0`; it makes the repository describe the current pre-release state accurately and consistently.

## Scope

F1 may change only release-facing documentation/metadata and its CI gate:

- root `README.md`;
- `web/README.md`;
- `CHANGELOG.md`;
- `docs/release_status.md`;
- `docs/governance/release_policy.md`;
- `REPOSITORY_MANIFEST.txt`;
- this specification;
- `tools/check_stage7_f1_release_docs_gate.py`; and
- the single Stage VII workflow invocation that executes the F1 gate.

`CITATION.cff` remains intentionally at version `0.0.0`. The application scientific core, validation corpus, runtime pins, dependency lockfile, AnalysisID/ExecutionID definitions, watchdogs, and econometric behavior are outside F1.

## Status-language contract

Repository-facing status must distinguish four concepts:

1. **Accepted baseline:** Stages III–VI.
2. **Current phase:** Stage VII release-hardening candidate.
3. **Later milestone:** Stage VIII Public Beta.
4. **Formal release:** Stage IX `v0.1.0`.

A public GitHub Pages URL does not itself imply Public Beta or a formal release. Stage VII remains pre-release until the final evidence/checklist, governed `main` integration, and required main-branch rerun pass.

## Citation contract

During Stage VII:

- `CITATION.cff` remains `version: 0.0.0`;
- no version-specific DOI is claimed;
- candidate deployment URLs are not described as scholarly releases; and
- formal citation language points to a future validated release actually used by the researcher.

## Repository-manifest contract

`REPOSITORY_MANIFEST.txt` is a newline-delimited, lexicographically sorted, duplicate-free inventory of all Git-tracked files. In CI the F1 gate compares it exactly with `git ls-files`.

This makes repository-structure drift explicit rather than allowing the manifest to lag behind release-hardening additions.

## CI contract

`tools/check_stage7_f1_release_docs_gate.py` must fail if:

- stale Stage VI-candidate language remains in the root/browser README;
- current status is promoted to Public Beta or formal `v0.1.0`;
- the release-status/release-policy documents omit the Stage VII→VIII→IX boundary;
- `CITATION.cff` ceases to be pre-release `0.0.0` or claims a DOI;
- the repository manifest is unsorted, duplicated, or differs from tracked files;
- the candidate application drops `noindex,nofollow` during Stage VII; or
- the Stage VII workflow stops invoking the F1 gate.

## Acceptance

F1 is accepted only when one exact commit passes Stages III–VII, including this gate and the existing production/live deployment verification.

Passing F1 does **not** complete Stage VII by itself. The formal Stage VII evidence/checklist remains the next bounded tranche.
