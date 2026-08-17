# Stage VII-D2 — Reproducibility Bundle Round Trip

Status: release-hardening candidate. D2 does **not** change the frozen Python scientific core, validation corpus, AnalysisID definition, ExecutionID definition, scientific runtime pins, or public-beta/release status.

## Purpose

D2 upgrades the browser reproducibility export from a deterministic ZIP writer into a closed-loop, privacy-preserving reproduction contract.

The bundle deliberately excludes the proprietary/raw research file. A full reproduction therefore requires:

1. the exported EFL reproducibility ZIP; and
2. the exact original local CSV used for the run.

The original research file remains local. D2 does not add upload, telemetry, persistence, or analysis-time network transmission.

## Bundle schema and integrity

D2 uses `EFL_REPRODUCIBILITY_BUNDLE_V2`.

The archive remains a deterministic stored ZIP: lexically ordered file names, UTF-8 names, no compression, fixed `1980-01-01` ZIP timestamps, no comments/extras, and standard CRC-32 per entry.

The reader is intentionally strict and accepts only the canonical stored-ZIP surface emitted by EFL. It rejects malformed boundaries, multi-disk archives, unsupported compression/metadata, unsafe or duplicate paths, non-canonical entry order/offsets, local/central disagreement, and CRC corruption.

`manifest.json` is the archive authority. It contains a SHA-256 payload inventory and a deterministic tree SHA-256 over the canonical payload-entry list. The payload set is fixed and excludes raw research data. `scientific_result.json` records the complete deterministic result returned by the authoritative Python core, and the manifest records its canonical scientific-result SHA-256.

The exporter must reopen and validate the just-created archive before returning bytes to the browser download boundary. A malformed or internally inconsistent bundle must fail closed.

## Upstream/downstream hash contract

The browser computes the SHA-256 of the exact normalized CSV sent to the Python engine. The scientific core independently records its `raw_file_sha256` for those same engine-input bytes.

D2 requires those two hashes to be identical before export. No fallback or silent substitution is permitted.

The bundle separately records:

- SHA-256 of the original local CSV bytes;
- SHA-256 of the normalized engine-input CSV;
- canonical-data SHA-256 from the scientific core; and
- locked-specification SHA-256 from the scientific core.

## Reconstruction contract

Given the bundle and original local CSV, the verifier must:

1. verify the ZIP structure, CRCs, exact payload set, per-payload SHA-256 values, and payload-tree SHA-256;
2. verify the original local-file SHA-256;
3. decode the original CSV as UTF-8 and apply the recorded source-column mapping;
4. reproduce the recorded explicit sorting decision without silent repair;
5. reproduce the normalized-to-original source-row provenance exactly;
6. reconstruct the engine-input CSV and require its SHA-256 to match both the browser manifest and the scientific core;
7. recover `analysis_spec.json` as the authoritative locked specification; and
8. verify the archived scientific result, scientific-core manifest, AnalysisID, ExecutionID, build commit, and scientific-result identity are internally consistent.

## Rerun contract

The validated local Pages candidate and the actual deployed HTTPS Pages site must execute a known-answer D2 round trip:

1. run KA-003 through the researcher UI;
2. export a D2 bundle;
3. reopen and validate the bundle;
4. verify the exact KA-003 original local CSV against the archive;
5. reconstruct the locked specification from `analysis_spec.json`;
6. start a new run from the same local source and relock the archived specification;
7. rerun through the existing validated browser Python engine;
8. require matching AnalysisID, ExecutionID, engine-input/canonical/specification hashes, build commit, and canonical scientific-result SHA-256;
9. require zero network requests during the reproduction rerun after the runtime is already initialized; and
10. export again and require the second ZIP to be byte-identical to the first.

This is a reproduction test, not a claim that a ZIP can reproduce proprietary data that it intentionally does not contain.

## Negative controls

Automated tests must reject at least:

- wrong original local file;
- corrupted ZIP bytes;
- unsafe archive paths;
- browser/core engine-input hash disagreement;
- altered manifest identifiers; and
- scientific-result drift after rerun.

## Frozen boundaries

D2 must not modify:

- `src/empirical_finance_lab/**`;
- `validation/**`;
- Pyodide/Python/NumPy/SciPy pins;
- runtime watchdogs;
- AnalysisID or ExecutionID formulas; or
- frontend runtime dependencies.

D2 remains Stage VII release hardening. Public Beta remains Stage VIII and formal `v0.1.0` release remains Stage IX.

Operational shorthand: **ZIP plus the exact original local CSV** is the required reproduction input pair.
