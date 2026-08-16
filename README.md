# Empirical Finance Lab

**Audit-first research software for credible, transparent, and reproducible empirical finance.**

> **Stage V CI candidate / pre-alpha:** Stage III and Stage IV remain the validated scientific baseline. A browser-runtime candidate now wraps the exact Python core through a pinned Pyodide module Web Worker. Stage V is **not accepted** until one commit passes Stage III, Stage IV, Stage V preflight, Chromium, Firefox, and WebKit.

## Scientific workflow

**Compute -> Audit -> Stress-test -> Interpret -> Reproduce**

The first module is the **Audit-First Event Study Analyzer** for one security and one event using daily returns. Its purpose is not merely to calculate AR/CAR, but to expose data validity, model assumptions, specification sensitivity, placebo evidence, inference assumptions, and reproducibility metadata.

## Current scientific core and Stage V CI candidate

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
- timeout/stale-execution lifecycle guards;
- pinned Pyodide module-Worker browser candidate with cross-runtime parity/privacy gates.

## Validation authority

The authoritative ground truth remains in `validation/` and predates the production core. The current implementation must conform to those fixtures; golden/reference outputs must **not** be regenerated merely because production code disagrees with them.

Run:

```bash
python tools/check_corpus_integrity.py
pytest -q
python tools/check_stage4_gate.py
python tools/check_stage5_static_gate.py
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
