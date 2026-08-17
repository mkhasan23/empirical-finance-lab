# Empirical Finance Lab

**Audit-first research software for credible, transparent, and reproducible empirical finance.**

> **Stage VI application-UI CI candidate / pre-alpha:** Stage III validation, Stage IV numerical core, and Stage V browser runtime are the validated scientific/runtime baseline. Stage VI adds the researcher-facing application workflow without changing the frozen Stage III corpus or Stage IV Python core. Stage VI is **not accepted** until one branch commit passes the Stage III, IV, V, and complete Stage VI Chromium/Firefox/WebKit gates.

## Scientific workflow

**Compute → Audit → Stress-test → Interpret → Reproduce**

The first module is the **Audit-First Event Study Analyzer** for one security and one event using daily returns. Its purpose is not merely to calculate AR/CAR, but to expose data validity, model assumptions, specification sensitivity, placebo evidence, inference assumptions, and reproducibility metadata.

## Validated scientific/runtime baseline

Implemented in `src/empirical_finance_lab/` and validated before the Stage VI interface:

- explicit CSV/unit/data validation with no silent imputation;
- trading-index event/estimation window construction;
- market model and market-adjusted model;
- AR and CAR;
- classical market-model predictive CAR inference;
- seeded PCG64 single-firm permutation inference;
- historical pre-event placebo diagnostic;
- prespecified robustness matrix;
- deterministic audit rules and Referee Mode;
- RawFileHash/CanonicalDataHash/SpecHash/AnalysisID/ExecutionID logic;
- pinned Pyodide module-Worker runtime with cross-browser parity/privacy validation;
- cancellation, stale-result rejection, worker-error propagation, and runtime watchdogs.

## Stage VI application candidate

The `web/` application now implements:

1. **Open local file** — no EFL research-data upload endpoint;
2. **Validate intake** — explicit column mapping, units, duplicate/date/order checks;
3. **Specify** — event identity, primary model/windows, inference, placebo, robustness;
4. **Lock** — methodological choices freeze for the run;
5. **Analyze** — the exact Stage IV Python core executes inside the validated Stage V worker;
6. **Audit** — PASS / WARNING / CRITICAL / NOT ASSESSABLE findings remain explicit;
7. **Stress-test** — prespecified robustness and historical placebo outputs;
8. **Interpret** — deterministic Referee Mode distinguishes association from causal attribution;
9. **Reproduce/Cite** — local reproducibility ZIP with hashes, specification, results, audits, environment, and pre-release citation status.

Stage VI does **not** re-estimate econometric quantities in TypeScript. Charts/tables display values returned by the scientific core.

## Validation authority

The authoritative ground truth remains in `validation/` and predates the production core. Golden/reference outputs must **not** be regenerated merely because production code disagrees with them.

Run from repository root:

```bash
python tools/check_corpus_integrity.py
pytest -q
python tools/check_stage4_gate.py
python tools/check_stage5_static_gate.py
python tools/check_stage6_static_gate.py
```

Stage VI additionally has TypeScript/Vitest/Vite and Playwright end-to-end gates in Chromium, Firefox, and WebKit.

## Scientific scope of v0.1

Supported:

- one security;
- one event;
- daily arithmetic returns;
- short-horizon event windows;
- market model primary;
- market-adjusted robustness;
- classical and permutation inference;
- historical placebo diagnostic;
- deterministic audit/reproducibility outputs.

Not supported: multi-firm CAAR inference, cross-sectional event-study tests, long-horizon BHAR, factor models, automated news/confounder detection, or causal certification.

## Important governance rule

Scientific changes are classified separately from software/reporting changes. Stage VI adds `docs/governance/stage6_frozen_scientific_tree.json`; its static gate fails if the Stage III validation corpus or Stage IV Python core changes on the UI branch.

## Citation

`CITATION.cff` is included from project inception. The current `0.0.0` pre-alpha state is **not a validated scholarly release** and has no version-specific DOI. Formal citation should use a future validated release and its exact DOI.

## License

BSD-3-Clause.
