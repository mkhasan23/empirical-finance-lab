# Stage VIII real-data validation evidence

This directory contains the **public, non-observation-level evidence** for the Empirical Finance Lab Stage VIII-C real-data parity exercise.

## Scientific purpose

Five prespecified real-company event studies were calculated from licensed CRSP daily returns and independently recomputed outside EFL. The same derived three-column inputs and locked specifications were then evaluated against the frozen EFL scientific-core algorithms at commit:

`ebbb1d0629f9fd1a128ff3d09f1494bbcaf1fb39`

All five cases passed the established EFL numerical parity tolerances.

## Frozen design

- Companies: MSFT, PG, NVDA, WMT, KO
- Expected-return model: market model
- Estimation window: `[-256,-46]`
- Event window: `[-1,+1]`
- Return units: decimal simple returns
- Direction: two-sided
- Permutation: `B=1000`
- RNG: PCG64
- Seed: `20260817`
- Placebo: off for this tranche
- Robustness variants: none for this tranche

## Data-license boundary

**No CRSP observation-level data are committed here.**

The original CRSP source file and the five derived three-column EFL input CSVs remain private/local. This directory records only:

- locked specifications;
- cryptographic hashes of private inputs;
- event-study outputs;
- numerical parity comparisons; and
- the immutable CRSP-source SHA-256 anchor.

The Stage VIII CI gate fails if a known private Stage VIII source/derived-input artifact is committed by exact SHA-256 or if a forbidden private-input filename appears in the repository.

## Evidence files

- `stage8c_manifest.json` — immutable input/result/specification hash registry.
- `stage8c_parity_results.json` — detailed external-vs-EFL parity comparisons.
- `stage8c_parity_results.csv` — compact tabular summary.
- `specifications/` — the five locked EFL specifications.

For methodology, case selection, event timing and limitations, see [`docs/STAGE_VIII_REAL_DATA_VALIDATION.md`](../../docs/STAGE_VIII_REAL_DATA_VALIDATION.md).
