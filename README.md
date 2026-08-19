# Empirical Finance Lab

**Audit-first research software for credible, transparent, and reproducible empirical finance.**

> **Current software line — v0.1.1 validated patch release line (formal).** The frozen scientific/external-validation baseline remains `a694d49df9716f9f87d359385598237363e4c3fc` (tree `621b0cafdcad3711d2aba3bef698d2e78d022144`). The immutable historical `v0.1.0` release remains fixed at `faf3dc6c5702dad3f5abd1dd15f7697fab5a5831`. The formal v0.1.1 release authority is the immutable `v0.1.1` tag at `55bc447141dde59853e670687bf46e383679eb78`, after exact-main and tag-context Stage III–X validation. The Stage VII release-engineering baseline remains `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.

**Live validated application:** https://mkhasan23.github.io/empirical-finance-lab/

**Archival DOI for exact v0.1.1:** [10.5281/zenodo.22018410](https://doi.org/10.5281/zenodo.22018410)

**Concept DOI for all EFL versions:** [10.5281/zenodo.22018409](https://doi.org/10.5281/zenodo.22018409)

Start with [`docs/quickstart.md`](docs/quickstart.md). For the current release boundary and acceptance record, see [`docs/release_status.md`](docs/release_status.md).

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
9. **Reproduce/Cite** — deterministic local reproducibility ZIP with hashes, specification, results, audits, environment, build provenance, and release-specific citation metadata.

The browser application does **not** re-estimate econometric quantities in TypeScript. Charts and tables display values returned by the scientific core.

## v0.1.1 interoperability and usability patch

v0.1.1 is a **non-econometric patch release**. It preserves the frozen Stage III/IV numerical authority and the accepted Stage VIII real-data evidence while improving researcher-facing interoperability, provenance, citation, and discoverability.

- browser intake deterministically accepts `YYYY-MM-DD`, `YYYY/MM/DD`, and `YYYYMMDD`;
- ambiguous `MM/DD/YYYY` versus `DD/MM/YYYY` is never guessed and requires an explicit researcher choice;
- date canonicalization occurs before duplicate/order/effective-trading-date checks and is locked into reproducibility provenance;
- CRSP-shaped headers `DlyCalDt`, `DlyRet`, and `vwretd` receive visible mapping suggestions;
- original local-file and normalized engine-input hashes remain separate;
- release citations are derived from the authoritative software version rather than a hardcoded tag;
- author/citation/search metadata, canonical URL, Search Console verification, and a sitemap improve public discoverability.

The general browser estimation-window default remains researcher-editable at `[-250,-30]`. The Stage VIII real-CRSP validation design `[-256,-46]` remains validation evidence, not a mandatory research default.

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

These controls form the **accepted Stage VII release-hardening baseline** at `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.

## Stage VIII accepted real-data external validation

Stage VIII adds a public-safe real-data validation evidence layer without changing the frozen numerical authority. Five heterogeneous CRSP event-study cases were independently recomputed from authorized local data and compared with the frozen EFL scientific core under one prespecified design. All scientific comparison fields passed the established browser-parity tolerances, and all five permutation extreme counts matched exactly.

The accepted Stage VIII external-validation baseline is `a694d49df9716f9f87d359385598237363e4c3fc` (tree `621b0cafdcad3711d2aba3bef698d2e78d022144`). Stages III–VIII passed on that exact merged `main` state; Stage VI's first main attempt encountered a transient WebKit cold-start/runtime stall, and the same-commit failed-job rerun passed without any source change.

Licensed CRSP observations and the five derived EFL input CSVs remain outside the public repository. Only locked specifications, hashes, numerical summaries, and public-safe parity evidence are committed. See [`docs/STAGE_VIII_REAL_DATA_VALIDATION.md`](docs/STAGE_VIII_REAL_DATA_VALIDATION.md).

Stage VIII supplies the real-data numerical validation evidence used by the v0.1.0 release line. It does not imply CRSP, WRDS, or any data vendor endorses or certifies EFL, and it does not convert event-study association into causal identification.

## v0.1.0 release validation

The v0.1.0 release line is backed by five heterogeneous real CRSP event-study cases that were independently recomputed outside the EFL production core under one prespecified design. The independently recomputed scientific quantities matched EFL within machine precision; the maximum absolute comparison delta was `2.7755575615628914e-16`, and all five permutation extreme counts matched exactly.

This is a **tested-case validation claim**, not a universal claim about every possible security, event, specification, dataset, or identification design. Licensed CRSP observations and the five derived EFL input CSVs are not distributed with the repository.

External feedback remains open after release. Use the repository's **Researcher feedback** issue form for workflow, documentation, browser/runtime, reproducibility, accessibility, or usability feedback. Never attach proprietary, licensed, confidential, or observation-level research data to a public issue; use a minimal synthetic reproduction where possible.

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
python tools/check_stage8_real_data_gate.py
python tools/check_stage9_release_gate.py
python tools/check_stage10_patch_release_gate.py
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

Scientific changes are classified separately from software/reporting changes. The frozen Stage VI scientific-tree manifest continues to protect the Stage III validation corpus and Stage IV Python core; Stage VIII owns and closes only its delegated `validation/real_data/` public-evidence subtree.

- Release policy: [`docs/governance/release_policy.md`](docs/governance/release_policy.md)
- Dependency policy: [`docs/governance/DEPENDENCY_UPDATE_POLICY.md`](docs/governance/DEPENDENCY_UPDATE_POLICY.md)
- Security/privacy boundary: [`SECURITY.md`](SECURITY.md)
- Contribution classifications: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Current release status: [`docs/release_status.md`](docs/release_status.md)

## Citation

`CITATION.cff` is configured for version `0.1.1` and records the exact version DOI `10.5281/zenodo.22018410`. The immutable `v0.1.0` tag remains historical release authority, while the immutable `v0.1.1` tag at `55bc447141dde59853e670687bf46e383679eb78` is the formal patch-release authority. The Concept DOI `10.5281/zenodo.22018409` represents the EFL software collection across versions.

Recommended exact-version citation: **Hasan, M. K. (2026). _Empirical Finance Lab: Audit-First Tools for Credible Empirical Finance Research_ (Version v0.1.1) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22018410**

Researchers reproducing or auditing v0.1.1 should cite the version-specific DOI rather than the all-versions Concept DOI.

## License

BSD-3-Clause.
