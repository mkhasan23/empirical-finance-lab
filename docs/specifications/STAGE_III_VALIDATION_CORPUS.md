# Empirical Finance Lab v0.1 — Stage III Validation Corpus and Repository Gate

**Status:** COMPLETE / PASS FOR STAGE IV IMPLEMENTATION

**Date:** 2026-08-16

## 1. Objective

Stage III establishes the repository structure and the authoritative ground truth *before* production econometric code. The future implementation must conform to these fixtures; the fixtures must never be retrofitted merely to make failing production code pass.

## 2. Repository authority hierarchy

1. Stage I scientific specification.
2. Stage II technical architecture.
3. Stage III methodological clarifications explicitly identified as operationalizations of Stage I.
4. Machine-readable schemas.
5. Authoritative validation fixtures and their independently derived outputs.
6. Production implementation (Stage IV and later).

If production code conflicts with levels 1–5, the code is presumed wrong until the conflict is resolved.

## 3. Corpus completed

- 5 known-answer fixtures (`KA-001`–`KA-005`).
- 2 inference fixtures (`INF-001`–`INF-002`).
- 1 hand-enumerable placebo fixture (`PLC-001`).
- 1 robustness fixture (`ROB-001`).
- 15 failure-mode/runtime fixtures (`FM-001`–`FM-015`).

Total authoritative fixtures: **24**.

## 4. Reference environment

Reference outputs were generated under Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0. These versions describe the Stage III reference calculation environment; they do not yet freeze the future public runtime dependency lock.

## 5. Independence controls

### Market-model coefficient fixtures
Analytical simple-regression formulas are compared with matrix normal equations.

### Classical CAR inference
`INF-001` is evaluated using both the scalar regression forecast-variance formula and general matrix predictive covariance.

### Permutation inference
`INF-002` includes both an exact enumeration over all distinct event-position assignments for a small fixture and a separately recorded seeded PCG64 Monte Carlo reference.

### Placebo diagnostic
`PLC-001` is deliberately small enough that every candidate pseudo-event and tail comparison can be inspected manually.

## 6. Clarification C-001

Stage I requires classical market-model inference to account for parameter-estimation uncertainty but did not write the exact CAR covariance expression. `docs/methodology/classical_inference_clarification.md` freezes that operational formula before production implementation. This is a clarification of the already-frozen scientific intent, not a new estimator.

## 7. Golden-output governance

A golden/reference output may change only when one of the following is documented:

- the previous reference is independently proven wrong;
- a formally approved methodology amendment changes the target; or
- an explicit numerical precision policy changes.

A production-code disagreement is **not** sufficient justification.

## 8. Release gate

Stage III passes only if:

- every required Stage II fixture ID exists;
- every fixture has machine-readable expected behavior;
- raw fixture files have SHA-256 fingerprints in `validation/manifest.json`;
- the integrity checker passes;
- no production event-study calculation code is present;
- citation/license/governance files exist;
- the current repository clearly identifies itself as pre-alpha/nonvalidated.

**Decision: PASS.** Stage IV may implement the numerical core against this corpus.
