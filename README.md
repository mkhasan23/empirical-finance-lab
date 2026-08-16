# Empirical Finance Lab

**Audit-first research software for credible, transparent, and reproducible empirical finance.**

> **Stage IV / pre-alpha:** The repository now contains a validated Python numerical core that reproduces the frozen Stage III reference corpus. It is **not yet** a formal scholarly release or public web application; Pyodide/browser parity and release validation remain outstanding.

## Scientific workflow

**Compute -> Audit -> Stress-test -> Interpret -> Reproduce**

The first module is the **Audit-First Event Study Analyzer** for one security and one event using daily returns. Its purpose is not merely to calculate AR/CAR, but to expose data validity, model assumptions, specification sensitivity, placebo evidence, inference assumptions, and reproducibility metadata.

## Current Stage IV core

Implemented in `src/empirical_finance_lab/`:

- explicit CSV/unit/data validation with no silent sorting or imputation;
- trading-index event/estimation window construction;
- market model and market-adjusted model;
- AR and CAR;
- classical market-model predictive CAR inference;
- seeded PCG64 single-firm permutation inference;
- historical pre-event placebo diagnostic;
- prespecified robustness matrix;
- deterministic audit rules and Referee Mode;
- RawFileHash, CanonicalDataHash, SpecHash, AnalysisID, and ExecutionID;
- timeout/stale-execution lifecycle guards for later browser integration.

## Validation authority

The authoritative ground truth remains in `validation/` and predates the production core. The current implementation must conform to those fixtures; golden/reference outputs must **not** be regenerated merely because production code disagrees with them.

Run:

```bash
python tools/check_corpus_integrity.py
pytest -q
python tools/check_stage4_gate.py
```

The Stage IV CI workflow pins the Stage III reference numerical environment for the gate: Python 3.13, NumPy 2.3.5, and SciPy 1.17.0.

## Scientific scope of v0.1

Supported core design:

- one security;
- one event;
- daily arithmetic returns;
- short-horizon event windows;
- market model primary;
- market-adjusted robustness;
- classical and permutation inference;
- historical placebo diagnostic;
- deterministic audit/reproducibility outputs.

Not yet supported: multi-firm CAAR inference, cross-sectional event-study tests, long-horizon BHAR, factor models, automated news/confounder detection, or causal certification.

## Important governance rule

Scientific changes are classified separately from software/reporting changes. A change to a golden/reference answer requires an independent derivation and explicit numerical-impact classification.

## Citation

`CITATION.cff` is included from project inception. The current `0.0.0` pre-alpha state is **not a validated scholarly release**. Formal citation should use a future version-specific DOI after browser/runtime/release validation.

## License

BSD-3-Clause.
