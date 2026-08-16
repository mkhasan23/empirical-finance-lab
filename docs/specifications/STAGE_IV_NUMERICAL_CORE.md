# Empirical Finance Lab v0.1 — Stage IV Validated Numerical Core

**Status:** COMPLETE / PASS FOR PRE-BROWSER INTEGRATION

**Date:** 2026-08-16

## 1. Objective

Stage IV implements the authoritative Python numerical core against the frozen Stage III validation corpus. The production implementation is subordinate to Stage I–III specifications and golden outputs.

## 2. Implemented modules

- `validation.py` — CSV parsing, explicit unit handling, data-integrity validation, no-silent-sort rule, canonicalization.
- `event_time.py` — confirmed trading-date mapping and inclusive estimation/event windows.
- `models.py` — market-model OLS with explicit rank/variance/df failures.
- `abnormal.py` — expected returns, AR, CAR, event-time path.
- `inference.py` — classical predictive CAR t inference and seeded PCG64 single-firm permutation inference.
- `diagnostics.py` — transparent inference-assumption diagnostics.
- `placebo.py` — deterministic pre-event pseudo-event enumeration and Historical Placebo Tail Proportion.
- `robustness.py` — prespecified model/window matrix without significance-driven selection.
- `audit.py` — stable rule IDs/statuses and deterministic Referee Mode templates.
- `reporting.py` — canonical data/spec hashing, AnalysisID, ExecutionID, reproducibility manifest.
- `runtime.py` — pure timeout/stale-execution guards for future browser worker integration.
- `engine.py` — end-to-end orchestration without UI or network assumptions.

## 3. Frozen numerical behavior reproduced

The Stage IV core reproduces all Stage III authoritative numerical fixtures within their frozen tolerances:

- KA-001 through KA-005;
- INF-001 and INF-002;
- PLC-001;
- ROB-001;
- FM-001 through FM-015 behavioral contracts.

The production code does not regenerate or rewrite any golden expected result.

## 4. Inference

### Classical market-model CAR

Stage IV implements Clarification C-001 exactly:

`Var_hat(CAR|X) = s^2 [m + x_sum' (X_est'X_est)^(-1) x_sum]`

and Student-t inference with `df=n-2`.

### Single-firm permutation

- explicit `numpy.random.Generator(numpy.random.PCG64(seed))`;
- identity permutation included first;
- `B` includes the identity permutation;
- market-model statistic uses `K=2`;
- market-adjusted statistic uses `K=0`;
- fixed seed/B reproduces the frozen INF-002 and ROB-001 outputs exactly.

## 5. Validation/failure behavior

No silent fixes are performed. In particular:

- duplicate dates block calculation;
- unsorted dates block calculation unless a separate explicit sort approval is supplied to canonicalization;
- missing event-window security/benchmark returns block complete CAR;
- missing estimation observations are pairwise excluded and counted;
- returns below -100% are invalid;
- extreme positive returns are preserved;
- an unconfirmed effective event date cannot execute;
- estimation/event overlap blocks execution;
- zero benchmark variance blocks the market model;
- a no-candidate placebo state does not destroy an otherwise valid primary result.

## 6. Reproducibility identity

Stage IV implements:

- RawFileHash;
- CanonicalDataHash;
- SpecHash;
- AnalysisID;
- ExecutionID.

CanonicalDataHash excludes source-row numbering so explicitly normalized but analytically identical data can share the same canonical analytical identity. RawFileHash separately preserves byte-level provenance.

## 7. Test suite

The Stage IV test suite covers:

- all 24 authoritative Stage III fixtures;
- exact and seeded permutation references;
- end-to-end integration;
- row-order normalization invariance;
- return-unit invariance;
- unused-metadata numerical invariance;
- robustness isolation;
- RNG isolation between primary permutation and placebo enablement;
- run-identity sensitivity;
- runtime timeout/stale-result contracts.

The authoritative test command is:

`pytest -q`

## 8. Runtime audit

On the documented development reference environment (Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0), the Stage IV test suite passes and representative workloads remain well inside Stage II's 45-second hard browser budget.

Performance measurements are engineering diagnostics, not guarantees for every user device. Pyodide/browser parity remains a later gate.

## 9. Explicit nonclaims

Stage IV is **not** yet:

- a public validated scholarly release;
- a browser application;
- Pyodide parity validated;
- a GitHub Pages deployment;
- a DOI release;
- a multi-firm event-study system.

## 10. Decision gate

**PASS.** The Python numerical core is ready to be committed as Stage IV and then subjected to the next integration step: package/build verification followed by pinned Pyodide parity and worker-boundary testing before any user-facing web interface is released.
