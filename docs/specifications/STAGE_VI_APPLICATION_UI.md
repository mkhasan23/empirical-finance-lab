# Empirical Finance Lab v0.1 — Stage VI Research Application Interface

**Status:** CI candidate until one commit passes Stage III, Stage IV, Stage V, Stage VI preflight, and Stage VI Chromium/Firefox/WebKit end-to-end gates.

## 1. Purpose

Stage VI turns the validated Stage IV numerical core and Stage V Pyodide/Web Worker runtime into a researcher-facing event-study application. It is an interface/reporting stage, not a methodological redesign.

The user workflow is:

**Open local file → Validate intake → Specify → Lock → Analyze → Audit → Stress-test → Interpret → Reproduce/Cite**

Stage VI must not re-estimate AR, CAR, model coefficients, inference, placebo outcomes, robustness outcomes, audit classifications, AnalysisID, or ExecutionID in TypeScript. Those values come from the validated Python core.

## 2. Frozen scientific boundary

The Stage III validation corpus and `src/empirical_finance_lab/` are byte-frozen against the Stage V validated baseline (`1a7aa82`). `docs/governance/stage6_frozen_scientific_tree.json` records SHA-256 hashes for every frozen scientific file, and the Stage VI static gate fails if any such file changes.

Stage VI may transform user-selected source columns into the three-column engine input required by the frozen core. This is a documented input-normalization operation, not econometric computation.

## 3. Local-data intake

The application reads a local UTF-8 CSV into browser memory. It does not contain an EFL research-data upload endpoint, telemetry, analytics, or remote crash reporting.

Required semantic mappings are:

- date;
- security return;
- benchmark return.

The interface records the original local-file SHA-256 before normalization. If source column names differ from the frozen engine schema, the browser constructs a deterministic engine-input CSV with headers `date,security_return,benchmark_return`.

The reproducibility bundle distinguishes:

- `raw_file_sha256`: original local-file bytes;
- `engine_input_sha256`: normalized/mapped bytes supplied to the scientific core;
- `canonical_data_sha256`: deterministic canonical dataset hash produced by the Python core;
- `specification_sha256`: locked specification hash produced by the Python core.

Raw proprietary input data are not included automatically in the reproducibility archive.

## 4. No silent sorting

Local intake may detect unsorted ISO dates. Sorting is never automatic. If the user explicitly approves ascending sorting, Stage VI records:

- that approval;
- normalized-to-original source-row provenance;
- the original raw-file hash;
- the normalized engine-input hash.

Duplicate dates remain blocking and are never auto-resolved.

## 5. Event-date confirmation

Stage VI may suggest an effective trading date using the observed mapped date sequence, but it cannot silently assign the date. The user must explicitly confirm the effective trading date before locking.

When timing is after market close, the next observed trading date is suggested. When timing is uncertain, the confirmed date is still accepted only with the core's uncertainty warning where applicable.

## 6. Prespecification and locking

Before execution the researcher specifies:

- return units;
- primary expected-return model;
- calendar event date;
- confirmed effective trading date;
- announcement timing;
- estimation window;
- primary event window;
- inference direction;
- permutation count;
- PCG64 seed;
- placebo enabled/disabled;
- known excluded dates;
- optional alternative model;
- up to three robustness windows.

Two-sided inference remains the default. One-sided inference requires an explicit acknowledgement that the directional hypothesis was prespecified.

The locked object is sent unchanged to the Stage V browser client. The Python core generates the authoritative SpecHash, AnalysisID, and ExecutionID.

## 7. Results and interpretation

Stage VI displays, without recomputation:

- main CAR;
- classical and permutation p-values;
- market-model diagnostics returned by the core;
- exact event-time return/AR/CAR rows;
- Research Integrity Audit;
- prespecified robustness matrix;
- historical placebo diagnostic;
- deterministic Referee Mode;
- run identifiers and reproducibility metadata.

Charts are visual representations of returned event-time/placebo values. Exact values remain available in tables or text.

The UI must not label a statistically significant CAR, an extreme placebo position, or a PASS audit as causal certification.

## 8. Reproducibility archive

Stage VI produces a deterministic, uncompressed ZIP with fixed ZIP timestamps and lexicographically ordered entries. The archive contains:

- `README.txt`
- `manifest.json`
- `analysis_spec.json`
- `normalization.json`
- `data_audit.json`
- `model_results.json`
- `event_time.csv`
- `inference.json`
- `robustness.csv`
- `placebo_summary.json`
- `placebo_events.csv`
- `audit_report.json`
- `referee_report.md`
- `environment.json`
- `citation.txt`

The archive does not include the original proprietary CSV unless a future specification explicitly adds an opt-in mechanism.

## 9. Accessibility and responsive behavior

The application uses native labels, fieldsets, legends, buttons, tables, headings, status regions, and keyboard-addressable tabs. Dynamic application status uses `role="status"`/`aria-live`, consistent with WCAG status-message guidance. Form errors are expressed in text rather than color alone.

Charts use SVG title/description elements and retain exact tabular/text alternatives. The layout must not horizontally overflow at a 390 px viewport except intentionally scrollable data tables.

Automated checks supplement rather than replace manual accessibility review.

## 10. Runtime/privacy invariants

- one active scientific analysis at a time;
- 45-second scientific-computation watchdog remains unchanged;
- progress-aware Stage V engine initialization remains unchanged;
- cancellation destroys the scientific worker;
- stale results are rejected;
- no application localStorage/sessionStorage persistence of research data;
- no analysis-time POST/PUT/PATCH/DELETE network requests;
- runtime requests are restricted by the Stage V parity/privacy gate.

## 11. Stage VI acceptance gate

Stage VI is not complete until the same branch commit passes:

1. Stage III corpus integrity;
2. Stage IV numerical core;
3. Stage V browser runtime parity;
4. Stage VI static/frozen-science gate;
5. TypeScript browser + Node/tooling type checks;
6. all Vitest unit tests;
7. production Vite build;
8. Stage VI full researcher journey in Chromium, Firefox, and WebKit;
9. Chromium extended robustness/placebo/Referee/export journey;
10. Chromium duplicate-date blocking journey;
11. Chromium mobile accessibility/responsiveness smoke.

The Stage VI CI candidate remains pre-alpha and must not be represented as a validated scholarly release until these gates are green on the same commit and the resulting branch is reviewed and squash-merged to `main`.
