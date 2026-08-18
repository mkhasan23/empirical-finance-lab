# Empirical Finance Lab

**Audit-first research software for credible, transparent, and reproducible empirical finance.**

> **Current status — Stage VII release hardening accepted on `main` (pre-release).** The accepted Stage VII baseline is exact `main` commit `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`, after governed integration and fresh Stage III–VII validation on `main`. Empirical Finance Lab is **not Public Beta**, and there is no formal `v0.1.0` release or version-specific DOI.

**Live validated pre-release application:** https://mkhasan23.github.io/empirical-finance-lab/

Start with [`docs/quickstart.md`](docs/quickstart.md). For the exact pre-release boundary and acceptance record, see [`docs/release_status.md`](docs/release_status.md).

## Scientific workflow

**Compute → Audit → Stress-test → Interpret → Reproduce**

The first module is the **Audit-First Event Study Analyzer** for one security and one event using daily returns. Its purpose is not merely to calculate AR/CAR, but to expose data validity, model assumptions, specification sensitivity, placebo evidence, inference assumptions, and reproducibility metadata.

## Accepted scientific/runtime baseline

Implemented in `src/empirical_finance_lab/` and protected from release-engineering drift:

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

## Researcher-facing application

The `web/` application implements:

1. **Open local file** — no EFL research-data upload endpoint;
2. **Validate intake** — explicit column mapping, units, duplicate/date/order checks;
3. **Specify** — event identity, primary model/windows, inference, placebo, robustness;
4. **Lock** — methodological choices freeze for the run;
5. **Analyze** — the authoritative Python core executes inside the validated worker;
6. **Audit** — PASS / WARNING / CRITICAL / NOT ASSESSABLE findings remain explicit;
7. **Stress-test** — prespecified robustness and historical placebo outputs;
8. **Interpret** — deterministic Referee Mode distinguishes association from causal attribution;
9. **Reproduce/Cite** — deterministic local reproducibility ZIP with hashes, specification, results, audits, environment, build provenance, and pre-release citation status.

The browser application does **not** re-estimate econometric quantities in TypeScript. Charts and tables display values returned by the scientific core.

## Stage VII accepted release hardening

Stage VII adds release engineering around the accepted scientific/application stack without adding econometric methods. Accepted Stage VII controls include:

- locked frontend dependency installation with `npm ci`;
- GitHub Pages production build and exact tested-artifact deployment;
- post-deployment byte-for-byte/live runtime verification;
- enforcing CSP/referrer policy and privacy/network checks;
- full-SHA GitHub Actions governance and controlled Dependabot scope;
- exact Git-commit build provenance propagated into browser and Python runtime metadata;
- privacy-preserving reproducibility ZIP round-trip with deterministic re-export;
- deterministic synthetic onboarding data tied to a frozen known answer;
- automated keyboard, hidden-state, and responsive checks at 320/390/768/1280 px.

These controls form the **accepted Stage VII pre-release baseline**. Acceptance does **not** promote the project to Public Beta or a formal scholarly release. Stage VIII remains the separate Public Beta / external-validation phase.

## Validation authority

The authoritative ground truth remains in `validation/` and predates the production core. Golden/reference outputs must **not** be regenerated merely because production code disagrees with them.

Core checks from repository root include:

```bash
python tools/check_corpus_integrity.py
pytest -q
python tools/check_stage4_gate.py
python tools/check_stage5_static_gate.py
python tools/check_stage6_static_gate.py
python tools/check_stage7_static_gate.py
python tools/check_stage7_d1_provenance_gate.py
python tools/check_stage7_e1_onboarding_gate.py
python tools/check_stage7_e2_accessibility_gate.py
python tools/check_stage7_f1_release_docs_gate.py
python tools/check_stage7_f2_evidence_gate.py
```

Browser/runtime/application gates additionally run TypeScript/Vitest/Vite and Playwright in their stage-specific workflows.

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

## Governance and security

Scientific changes are classified separately from software/reporting changes. The frozen Stage VI scientific-tree manifest continues to protect the Stage III validation corpus and Stage IV Python core.

- Release policy: [`docs/governance/release_policy.md`](docs/governance/release_policy.md)
- Dependency policy: [`docs/governance/DEPENDENCY_UPDATE_POLICY.md`](docs/governance/DEPENDENCY_UPDATE_POLICY.md)
- Security/privacy boundary: [`SECURITY.md`](SECURITY.md)
- Contribution classifications: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Current release status: [`docs/release_status.md`](docs/release_status.md)

## Citation

`CITATION.cff` intentionally remains at `0.0.0` while the project is pre-release. There is no version-specific DOI. Formal scholarly citation should use a future validated release and its exact release metadata rather than treating the accepted Stage VII pre-release deployment as a formal release.

## License

BSD-3-Clause.
