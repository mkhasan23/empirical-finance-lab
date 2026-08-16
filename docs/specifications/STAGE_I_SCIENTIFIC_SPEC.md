---
title: "Empirical Finance Lab v0.1"
subtitle: "Audit-First Event Study Analyzer — Authoritative Research, Methodology, Validation, and Product Specification"
author: "Muhammad Kamrul Hasan"
date: "16 August 2026"
---

# Document Status

**Specification status:** FROZEN FOR IMPLEMENTATION  
**Version:** Design Specification 0.1  
**Project:** Empirical Finance Lab (EFL)

# 1. Mission

**Empirical Finance Lab (EFL)** is an open-source, audit-first research-software project designed to help researchers produce empirical-finance evidence that is:

- computationally correct;
- methodologically transparent;
- diagnostically auditable;
- specification-aware;
- reproducible; and
- appropriately interpreted.

The organizing principle is:

$$
\boxed{\text{Compute}\rightarrow\text{Audit}\rightarrow\text{Stress-test}\rightarrow\text{Interpret}\rightarrow\text{Reproduce}}
$$

EFL must never optimize an analysis toward statistical significance. Its objective is to determine the result implied by the supplied data and specification and to identify conditions that weaken confidence in that result.

# 2. First Product

The first public module is:

**Empirical Finance Lab v0.1 — Audit-First Event Study Analyzer**

The application evaluates **one security and one economic event at a time using daily returns**.

This deliberate restriction prevents v0.1 from mixing single-event inference with methods developed for cross-sectional samples of many firms.

Classical event-study methodology separates the estimation window from the event window and uses an expected-return model to construct abnormal returns. MacKinlay (1997) remains a foundational reference, while Brown and Warner (1985) establish the practical use of daily return data in event studies.

# 3. Intellectual Positioning

EFL v0.1 is **not merely an event-study calculator**.

Its distinctive research contribution is the integration of:

1. event-study computation;
2. deterministic research-integrity auditing;
3. specification robustness;
4. formal single-firm permutation inference;
5. pseudo-event placebo diagnostics;
6. conservative interpretation;
7. reproducibility-by-construction; and
8. referee-style methodological reporting.

The central question is therefore not merely:

> **What is the abnormal return?**

but also:

> **How credible is this result under the stated data, model, inference procedure, and alternative defensible specifications?**

EFL must not claim to be the first event-study platform or first open-source empirical-finance tool unless future systematic evidence establishes such a claim.

# 4. Governing Scientific Principles

## 4.1 Truth before convenience

The software must report unfavorable diagnostics even when they weaken a statistically significant result.

## 4.2 No silent repairs

The application must never silently:

- impute event-window returns;
- delete duplicate observations;
- shift event dates;
- change event windows;
- change model specifications;
- winsorize observations;
- substitute benchmarks; or
- alter return units.

Any necessary correction requires either explicit user action or an explicitly recorded rule.

## 4.3 Computation is not identification

A statistically significant CAR demonstrates an unusual return conditional on the maintained event-study model and inference assumptions.

It does **not automatically establish that the event causally generated the return**.

Accordingly:

$$
\boxed{\text{Significant CAR}\not\Rightarrow\text{Causal effect established}}
$$

## 4.4 No universal credibility score

EFL will **not** generate an overall score such as "86/100."

Serious methodological failures cannot legitimately be averaged against unrelated successful diagnostics.

# 5. Scope of v0.1

## 5.1 Supported

- single security;
- single event;
- daily arithmetic returns;
- one benchmark return series;
- user-defined event date;
- user-defined estimation window;
- short-horizon event windows;
- market model;
- market-adjusted model;
- abnormal return (AR);
- cumulative abnormal return (CAR);
- classical model-based inference;
- permutation inference;
- historical pseudo-event placebo analysis;
- data-integrity diagnostics;
- specification robustness;
- reproducibility export; and
- deterministic Referee Mode.

## 5.2 Explicitly not supported in v0.1

- multiple securities;
- multiple events;
- AAR;
- CAAR;
- cross-sectional CAR regressions;
- Patell cross-sectional tests;
- BMP cross-sectional tests;
- Kolari-Pynnönen cross-correlation corrections;
- intraday returns;
- long-horizon BHAR analysis;
- CAPM;
- Fama-French 3-factor model;
- Fama-French 5-factor model;
- momentum-factor models;
- synthetic-control event studies;
- automatic news/confounding-event detection;
- causal certification;
- automatic price-to-return construction;
- automated CRSP/Compustat/WRDS access; and
- AI-generated numerical calculations.

Cross-sectional dependence is a material issue when events cluster across firms. Because v0.1 contains only one security/event, cross-sectional procedures are deliberately reserved for the future multi-event module.

# 6. Required Input Contract

The minimum dataset contains:

| Field | Requirement |
|---|---|
| `date` | Unique daily observation date |
| `security_return` | Arithmetic security return |
| `benchmark_return` | Arithmetic benchmark return |

The user separately specifies:

- announced calendar date;
- effective event trading day;
- announcement timing if known;
- estimation window;
- primary event window;
- robustness event windows;
- expected-return model;
- return units;
- optional known confounding-event dates; and
- optional data-source metadata.

## 6.1 Return units

EFL must never infer whether `5` means 5% or 500%.

The user must explicitly identify whether the uploaded data are:

- decimal returns, e.g., `0.05`; or
- percentage returns, e.g., `5.0`.

All internal calculations use decimal returns.

## 6.2 Return definition

v0.1 supports **simple arithmetic returns only**.

The app does not infer or construct total returns from raw prices.

## 6.3 Date uniqueness

Each date must occur at most once.

Duplicate dates produce:

**CRITICAL — DUPLICATE DATE OBSERVATIONS**

Analysis is blocked until resolved.

## 6.4 Impossible simple returns

For simple returns,

$$
R_t < -1
$$

is mathematically invalid and triggers a critical error.

Large positive returns are permitted but may trigger an outlier diagnostic.

# 7. Trading-Day Construction

The observed benchmark-return calendar defines the candidate trading-day sequence.

EFL must not assume that every Monday-Friday date is necessarily a trading day.

A missing security return on an otherwise valid benchmark trading day is treated as missing, not as zero.

# 8. Event-Date Alignment

Event-date handling is potentially consequential and therefore cannot occur silently.

The user provides:

1. calendar announcement date; and
2. effective event trading date.

EFL may **suggest** an effective trading date, but the user must confirm it before analysis.

For example:

- announcement before or during trading: same trading day may be appropriate;
- announcement after market close: next trading day may be appropriate;
- weekend or holiday announcement: next trading day may be appropriate.

The confirmed mapping is stored in the reproducibility record.

If announcement timing is unknown:

**WARNING — EVENT-TIME ALIGNMENT UNCERTAIN**

The application should encourage robustness windows that span the ambiguity.

# 9. Estimation and Event Windows

Event time is indexed relative to the confirmed event trading day:

$$
\tau=0.
$$

## 9.1 Product default

The initial default configuration is:

$$
\text{Estimation Window}=[-250,-30]
$$

and

$$
\text{Primary Event Window}=[-1,+1].
$$

These are **software defaults rather than claims of universally optimal methodology**.

Users may change them before the analysis is run.

## 9.2 Contamination gap

The estimation window must not overlap the event window.

A pre-event gap between the estimation sample and event period is recommended to reduce contamination from information leakage or anticipation.

## 9.3 v0.1 event-window boundary

v0.1 is explicitly a **short-horizon event-study tool**.

The public research-grade interface supports event windows containing no more than **11 trading days**.

This is an EFL scope restriction, not a claim that eleven days is a universal econometric cutoff.

Long-horizon event studies require additional methodological treatment and belong outside v0.1.

# 10. Estimation-Sample Sufficiency

There is no universally correct fixed minimum estimation-window length.

EFL therefore reports the exact usable observation count.

For the market model, the following are **EFL operational safeguards**, not universal statistical constants:

$$
N_{\mathrm{est}} < 60 \quad \Rightarrow \quad \text{CRITICAL research-quality warning}
$$

$$
60 \le N_{\mathrm{est}} < 120 \quad \Rightarrow \quad \text{WARNING}
$$

$$
N_{\mathrm{est}} \ge 120 \quad \Rightarrow \quad \text{no sample-length warning}
$$

The software may calculate an exploratory result below 60 observations if estimation is mathematically feasible, but Referee Mode must state that the estimation history is short and cannot classify the analysis as research-grade.

The exact threshold policy must be disclosed in the documentation.

# 11. Expected-Return Models

## 11.1 Market Model — Primary

The primary model is:

$$
R_{it}=\alpha_i+\beta_iR_{mt}+\epsilon_{it},
$$

where:

- $R_{it}$ = security return;
- $R_{mt}$ = benchmark return;
- $\alpha_i$ = intercept;
- $\beta_i$ = benchmark sensitivity; and
- $\epsilon_{it}$ = residual.

Parameters are estimated **only over the estimation window**.

The event-period expected return is:

$$
\widehat{R}_{it}=\widehat{\alpha}_i+\widehat{\beta}_iR_{mt}.
$$

Abnormal return is:

$$
AR_{it}=R_{it}-\widehat{R}_{it}.
$$

## 11.2 Market-Adjusted Model — Robustness

The market-adjusted specification is:

$$
AR_{it}=R_{it}-R_{mt}.
$$

This is equivalent to a restricted market model imposing:

$$
\alpha_i=0,
\qquad
\beta_i=1.
$$

# 12. Cumulative Abnormal Returns

For event window $[\tau_1,\tau_2]$, the cumulative abnormal return is:

$$
CAR_i[\tau_1,\tau_2]=\sum_{\tau=\tau_1}^{\tau_2}AR_{i\tau}.
$$

EFL reports:

- event-time date;
- actual security return;
- expected return;
- abnormal return; and
- cumulative abnormal return.

No event-window missing return may be silently ignored.

# 13. Missing-Data Policy

## 13.1 Estimation window

Observations missing either security or benchmark returns are excluded pairwise.

EFL reports:

- requested estimation observations;
- usable observations;
- dropped observations; and
- missingness percentage.

Material missingness generates a warning.

## 13.2 Event window

If either required return is missing for an event-window date:

**CRITICAL — EVENT WINDOW INCOMPLETE**

CAR for any window containing that observation is **not reported as complete**.

EFL does not replace missing event returns with zero.

# 14. Outlier Policy

EFL does **not winsorize automatically**.

The application may identify statistically unusual observations using a robust diagnostic, but the raw return remains unchanged.

Outlier status therefore means:

> **Inspect this observation.**

It does not mean:

> **Delete this observation.**

Any user-directed exclusion creates a new analysis specification and new run identifier.

# 15. Primary Statistical Inference

v0.1 deliberately separates:

1. classical model-based inference; and
2. nonparametric permutation inference.

Daily returns can exhibit non-normality, and traditional parametric tests may become unreliable under some conditions. Corrado (1989) develops nonparametric rank-based event-study inference, while Nguyen and Wolf develop single-firm permutation inference.

## 15.1 Classical inference

For the market model, EFL estimates residual variance from the estimation period and accounts for estimation uncertainty when standardizing event-period abnormal returns/CAR.

The output reports:

- test statistic;
- degrees of freedom where applicable;
- two-sided p-value; and
- maintained assumptions.

Classical inference is **not** labeled assumption-free.

Event-induced increases in variance can cause commonly used methods to reject too frequently; therefore event-period variance changes are a material inferential concern.

## 15.2 Default hypothesis

Unless direction was genuinely prespecified before results are seen:

$$
H_0:E(CAR)=0
$$

against

$$
H_1:E(CAR)\neq0.
$$

Therefore, EFL defaults to **two-sided inference**.

A one-sided test requires explicit pre-analysis selection and is permanently recorded in the run specification.

# 16. Single-Firm Permutation Test

This becomes a major v0.1 credibility feature.

Let:

- $n$ = estimation-window observations; and
- $m$ = event-window observations.

Construct the combined abnormal-return sequence from the estimation and event windows.

For a two-sided test, define the observed statistic using the absolute standardized CAR.

The combined observations are repeatedly permuted, the statistic is recalculated, and the permutation p-value is the fraction of permuted statistics at least as extreme as the observed statistic.

EFL default:

$$
B=20{,}000
$$

permutations for normal use.

A higher user-selected value is permitted.

The reproducibility bundle records:

- $B$;
- random seed;
- test direction;
- test statistic; and
- resulting permutation p-value.

## 16.1 Critical assumption disclosure

The finite-sample validity result relies on the relevant abnormal returns being exchangeable under the null; in the cited single-firm framework, the combined abnormal returns are assumed i.i.d. with common mean zero and variance.

Accordingly, EFL must never present permutation inference as universally assumption-free.

Evidence of substantial serial dependence or variance instability triggers an explicit warning.

# 17. Placebo Event Diagnostic

This is distinct from the formal permutation test.

The question is:

> **Would similarly large CARs commonly appear around false event dates in this security's own history?**

## 17.1 Candidate pseudo-events

A pseudo-event date is admissible only if:

- it is a valid trading day;
- its complete requested event window exists;
- a valid estimation window exists before it;
- it does not overlap the actual event window;
- it does not overlap user-supplied excluded/confounding periods; and
- it satisfies the same data-completeness requirements as the true event.

## 17.2 Identical specification

Every placebo event must use exactly the same:

- benchmark;
- return model;
- estimation-window length;
- estimation-to-event gap;
- event-window structure; and
- missing-data rules.

The placebo procedure cannot be modified to make the actual event appear more unusual.

## 17.3 Historical placebo distribution

For every admissible pseudo-event $p$:

$$
CAR^{P}_p[\tau_1,\tau_2]
$$

is calculated.

Whenever computationally feasible, **all admissible pseudo-events are used**.

If sampling is required for computational reasons:

- the sampling rule must be deterministic conditional on a stored random seed; and
- requested and realized placebo counts must be recorded.

## 17.4 Historical Placebo Tail Proportion

For two-sided comparison:

$$
q_{\mathrm{placebo}}
=
\frac{
1+\sum_{p=1}^{P}
I\left(
\left|CAR_p^{P}\right|
\ge
\left|CAR^{\mathrm{Actual}}\right|
\right)
}{P+1}.
$$

EFL labels this:

**Historical Placebo Tail Proportion**

and not automatically:

**causal p-value**.

The pseudo-event-date distribution may be affected by:

- time-varying volatility;
- regime changes;
- serial dependence;
- unknown historical confounding events; and
- nonstationarity.

Therefore:

$$
\boxed{\text{Extreme placebo position}\not\Rightarrow\text{causality established}}
$$

## 17.5 Interpretation

**Placebo evidence: unusual**

> The observed CAR lies in the extreme tail of the admissible historical pseudo-event distribution.

**Placebo evidence: not unusual**

> Similar-magnitude CARs occur frequently around admissible pseudo-event dates.

The continuous tail proportion is always displayed; categorical language is secondary.

# 18. Specification Robustness Framework

Robustness analysis must not become automated specification mining.

## 18.1 Pre-analysis locking

Before calculation, the user specifies:

- primary model;
- primary event window;
- robustness model(s);
- robustness event window(s); and
- inference direction.

Once results have been generated, changing one of these choices creates a **new Run ID**.

The prior specification remains preserved.

## 18.2 v0.1 model robustness

Compare:

- market model; and
- market-adjusted model.

## 18.3 Event-window robustness

The user may prespecify up to three secondary short-horizon event windows.

Examples may include:

$$
[0,0],\qquad[-1,+1],\qquad[-2,+2].
$$

These are examples, not mandatory universal specifications.

## 18.4 Robustness dimensions

For every specification EFL records:

### Sign stability

Does the sign of CAR remain unchanged?

### Magnitude stability

How materially does CAR change?

### Inferential stability

Does the statistical conclusion depend on specification?

EFL does **not** search across specifications and then select the most significant result.

# 19. Robustness Matrix

A canonical output is:

| Model | Window | CAR | Classical p | Permutation p | Sign |
|---|---|---:|---:|---:|---|
| Primary model | Primary window | — | — | — | — |
| Alternative model | Primary window | — | — | — | — |
| Primary model | Alternative window 1 | — | — | — | — |
| Primary model | Alternative window 2 | — | — | — | — |

The software then describes the pattern conservatively.

**High robustness**

> Sign, magnitude, and inference are broadly stable across prespecified alternatives.

**Moderate robustness**

> Sign is stable, but inferential strength varies across specifications.

**Low robustness**

> Sign or economic magnitude changes materially across defensible specifications.

No robustness classification is permitted to hide the underlying numerical matrix.

# 20. Data-Integrity Audit

Every run checks at minimum:

- malformed dates;
- duplicate dates;
- unsorted dates;
- missing security returns;
- missing benchmark returns;
- invalid return units;
- simple returns below $-100\%$;
- insufficient estimation observations;
- incomplete event window;
- estimation/event overlap;
- unexplained gaps;
- extreme-return observations; and
- event-date alignment uncertainty.

# 21. Model-Integrity Audit

For the market model, EFL reports:

- $\widehat{\alpha}$;
- $\widehat{\beta}$;
- $R^2$;
- residual standard deviation;
- usable $N$;
- residual serial-correlation diagnostics;
- heteroskedasticity/variance-instability diagnostics where supported; and
- influential-observation indicators where supported.

A low $R^2$ is not automatically a model failure.

The software reports it rather than imposing an arbitrary universal cutoff.

# 22. Event-Induced Variance Warning

Because event-period variance changes can distort conventional inference, EFL must distinguish:

- estimation-period residual volatility; and
- unusually large event-period residual movements.

For a single event, EFL cannot reliably estimate an entirely new event-period variance regime from a few observations.

Therefore the correct v0.1 response is:

**WARNING — POSSIBLE EVENT-INDUCED VARIANCE**

rather than a falsely precise correction.

# 23. Confounding-Event Audit

v0.1 has no external news database.

Therefore it cannot truthfully state:

> **No confounding events occurred.**

### If the user supplies competing-event information

EFL evaluates temporal overlap and reports it.

### If the user does not

Status:

**NOT ASSESSABLE — EXTERNAL CONFOUNDING EVENTS NOT PROVIDED**

Lack of evidence is not converted into a PASS.

# 24. Audit States

Every diagnostic receives exactly one of four statuses:

### PASS

The specified check was performed and no material problem was detected.

### WARNING

A condition exists that may weaken interpretation but does not mechanically invalidate calculation.

### CRITICAL

A condition prevents the requested result from being regarded as valid under the stated specification.

### NOT ASSESSABLE

The software lacks the necessary information to evaluate the issue.

No fifth "probably okay" state is permitted.

# 25. Referee Mode

Referee Mode is a **deterministic synthesis layer**, not an unconstrained language model.

Its claims must map directly to measured diagnostics.

Canonical output:

| Dimension | Example status |
|---|---|
| Computational validity | PASS |
| Data integrity | PASS |
| Event-time alignment | WARNING |
| Model stability | PASS |
| Specification robustness | MODERATE |
| Permutation inference | SUPPORTIVE / NOT SUPPORTIVE / ASSUMPTION WARNING |
| Historical placebo evidence | UNUSUAL / NOT UNUSUAL |
| Confounding events | NOT ASSESSABLE |
| Causal interpretation | NOT ESTABLISHED |

It then provides a concise explanation of each status.

Referee Mode must never say:

> **This proves the event caused the stock-price reaction.**

unless a future research design contains separate identification sufficient to justify such a claim.

# 26. Interpretation Hierarchy

EFL distinguishes four levels:

## Level 1 — Computation

> CAR equals $x\%$.

## Level 2 — Statistical evidence

> CAR is inconsistent with the stated zero-abnormal-return null under the selected inference procedure and maintained assumptions.

## Level 3 — Event association

> The security experienced an unusual return around the identified event.

## Level 4 — Causal attribution

> The event caused the return.

v0.1 may support Levels 1-3 depending on the evidence.

It does **not automatically certify Level 4**.

# 27. Known-Answer Validation Framework

No numerical engine may be released merely because it executes successfully.

## 27.1 Deterministic synthetic cases

Create synthetic return series with known:

- $\alpha$;
- $\beta$;
- residual variance;
- event abnormal return; and
- CAR.

Example conceptual data-generating process:

$$
R_{it}=0.001+1.2R_{mt}+\epsilon_t
$$

with deliberately controlled $\epsilon_t$.

A known abnormal return is then injected into the event window.

The expected result is calculated independently before implementation testing.

## 27.2 Zero-effect case

Construct data where:

$$
AR_{\tau}=0
$$

for all event dates.

Required result:

$$
CAR=0
$$

within numerical tolerance.

## 27.3 Known positive-event case

Inject known:

$$
AR_0=0.05.
$$

Required event-day result:

$$
AR_0=5\%.
$$

## 27.4 Multi-day CAR case

Inject:

$$
AR_{-1}=1\%,\qquad AR_0=3\%,\qquad AR_{+1}=-1\%.
$$

Required:

$$
CAR[-1,+1]=3\%.
$$

# 28. Failure-Mode Test Suite

The application must be deliberately tested against defective input.

Required cases include:

1. duplicate dates;
2. unsorted dates;
3. event on non-trading calendar date;
4. uncertain after-hours event;
5. missing event-day security return;
6. missing benchmark return;
7. incomplete event window;
8. insufficient estimation history;
9. overlapping estimation/event windows;
10. security return below $-100\%$;
11. ambiguous return units;
12. extreme positive return;
13. benchmark with gaps;
14. placebo date lacking adequate estimation history;
15. no admissible placebo dates; and
16. user changes specification after results are observed.

Every case receives a predetermined expected software response.

# 29. Independent Numerical Validation

Before public release, every primary calculation must be validated against at least two independent standards wherever feasible:

1. hand or analytical calculation on small known-answer data; and
2. an independent established implementation or independently written reference calculation.

Any discrepancy beyond declared floating-point tolerance must be investigated.

The discrepancy cannot be resolved merely by choosing the result produced by EFL.

# 30. Runtime-Risk Requirements

The application is not considered release-ready unless it contains runtime safeguards.

At minimum:

- schema validation;
- finite-number validation;
- dimension checks;
- duplicate checks;
- estimation-sample checks;
- event-window checks;
- deterministic random-seed handling;
- permutation-count validation;
- explicit exception handling; and
- no partial-result presentation after a critical computational failure.

If the numerical engine fails, the UI must not display stale results from a previous run.

# 31. Reproducibility Bundle

Every completed analysis may export a bundle containing:

## 31.1 Analysis specification

- software version;
- Run ID;
- analysis timestamp;
- model;
- estimation window;
- event window;
- robustness windows;
- event-date mapping;
- return units; and
- test direction.

## 31.2 Data audit

- input row count;
- usable row count;
- exclusions;
- missingness;
- duplicate status; and
- warnings.

## 31.3 Estimation results

- coefficients;
- model diagnostics;
- AR;
- CAR; and
- test statistics.

## 31.4 Permutation metadata

- $B$;
- seed;
- p-value; and
- assumptions/warnings.

## 31.5 Placebo metadata

- candidate-date rule;
- candidate count;
- exclusions;
- realized placebo count;
- placebo distribution summary; and
- tail proportion.

## 31.6 Robustness results

- all prespecified models/windows; and
- numerical comparison.

## 31.7 Citation information

- EFL version;
- DOI once assigned; and
- formatted software citation.

# 32. Reproducibility Identity

Every analysis receives a unique **Run ID** derived from the analysis configuration and appropriate metadata.

Changing a material methodological setting creates a new run.

This prevents silent overwriting of the specification that generated a reported result.

# 33. Software Versioning

EFL will use semantic versioning conceptually:

$$
\text{MAJOR.MINOR.PATCH}.
$$

Methodological changes capable of altering reported research results must be clearly documented.

Release notes must state whether a change affects:

- calculations;
- diagnostics;
- inference;
- placebo procedures; or
- reporting only.

Researchers must be able to determine which software version generated their published result.

# 34. Citation Architecture

EFL will be designed as a citable scholarly software output.

Before the first formal scholarly release, EFL will contain:

- `CITATION.cff`;
- explicit software authorship;
- project title;
- version;
- release date;
- repository reference;
- ORCID identifier(s), where available;
- Zenodo DOI; and
- recommended version-specific citation.

Formal GitHub releases should be archived so researchers can cite the exact software version used.

The citation architecture follows standard scholarly-software principles emphasizing credit, persistent identification, accessibility, and specificity.

# 35. Citation Philosophy

The application may state:

> **If Empirical Finance Lab materially contributes to your research, please cite the software using the version-specific citation provided with your results.**

It must not imply that citation is payment for free access.

Citation should reflect substantive methodological use.

# 36. Future Software Paper

A formal software paper becomes appropriate only after the platform has:

- a mature research application;
- meaningful functionality;
- documented methodology;
- automated tests;
- user documentation;
- demonstrated research use; and
- stable open-source release history.

A software-paper submission is therefore a **future objective**, not something EFL v0.1 will prematurely claim eligibility for.

# 37. Privacy Principle

Research data should be exposed to the minimum infrastructure necessary.

Preferred v0.1 architecture:

- client-side computation where technically practical;
- no permanent upload storage;
- no user-data resale;
- no hidden training use; and
- clear disclosure of any server-side processing if later required.

The final architecture must document actual behavior rather than make an unsupported "local-only" claim.

# 38. Open-Source Requirement

The public research version must use an OSI-compatible open-source license before formal release.

The exact license is **not frozen in this specification** because software architecture, dependency licenses, contribution policy, and possible future distribution need to be reviewed first.

This unresolved choice does not block methodology development.

# 39. v0.1 Primary User Workflow

The intended sequence is:

1. Upload daily security and benchmark returns.
2. Map required columns and explicitly declare units.
3. Run input/data-integrity validation.
4. Enter calendar event date and confirm effective trading date.
5. Prespecify primary model, estimation window, primary event window, robustness windows, and inference direction.
6. Lock the run specification.
7. Estimate expected returns.
8. Calculate AR and CAR.
9. Run classical and permutation inference.
10. Run integrity diagnostics.
11. Run prespecified robustness analysis.
12. Run historical pseudo-event placebo diagnostic.
13. Generate Referee Mode.
14. Export reproducibility bundle and citation.

# 40. Canonical Results Screen

The primary results screen should prioritize:

## 40.1 Main Estimate

$$
CAR[\tau_1,\tau_2]
$$

with:

- event window;
- model;
- estimate;
- classical statistic/p-value; and
- permutation p-value.

## 40.2 Event-Time Plot

Daily abnormal return:

$$
AR_{\tau}
$$

and cumulative abnormal return:

$$
CAR_{\tau}.
$$

## 40.3 Research Integrity

PASS / WARNING / CRITICAL / NOT ASSESSABLE.

## 40.4 Robustness Matrix

All prespecified alternatives.

## 40.5 Placebo Distribution

Observed CAR marked against historical pseudo-event CARs.

## 40.6 Referee Mode

Conservative synthesis.

## 40.7 Reproduce / Cite

Download reproducibility information and version-specific citation.

# 41. Explicit Prohibited Behaviors

EFL v0.1 must never:

- choose the event window yielding the smallest p-value;
- automatically discard observations to improve significance;
- call a robustness test "passed" merely because $p<0.05$;
- claim no confounders when none were supplied;
- infer causal identification from statistical significance;
- conceal specification sensitivity;
- report partial CAR as complete CAR;
- silently shift dates;
- silently impute returns;
- use an LLM to calculate numerical estimates;
- fabricate methodological citations; or
- change a frozen run specification without generating a new run.

# 42. v0.1 Acceptance Criteria

Public release is prohibited until all of the following hold.

## 42.1 Mathematical validation

- market-model coefficients match known-answer cases;
- expected returns match independent calculations;
- AR matches independent calculations;
- CAR matches independent calculations;
- classical inference matches independently derived references;
- permutation implementation reproduces known test cases; and
- placebo calculation reproduces known cases.

## 42.2 Input validation

Every required failure-mode test behaves exactly as specified.

## 42.3 Reproducibility

Running identical:

- data;
- specification;
- software version; and
- random seed

produces identical numerical results.

## 42.4 Specification integrity

Changing any material analysis setting generates a different run identity.

## 42.5 Audit integrity

No critical condition is presented as PASS.

## 42.6 Interpretation integrity

No output equates statistical significance with causal proof.

## 42.7 Documentation

Every reported statistic has:

- mathematical definition;
- input definition;
- assumption statement; and
- methodological source where applicable.

## 42.8 Citation

Formal release contains valid citation metadata and archived version information.

# 43. Authoritative v0.1 Methodological Hierarchy

When methodological signals conflict, EFL uses the following hierarchy:

$$
\boxed{\text{Data validity}>\text{Specification validity}>\text{Inference validity}>\text{Statistical significance}}
$$

A significant coefficient or CAR cannot override a critical data failure.

Likewise:

$$
\boxed{\text{Correct null result}>\text{Incorrect significant result}}
$$

# 44. Internal Consistency Audit of This Specification

The specification itself has been audited before implementation.

## 44.1 Single-event design versus cross-sectional tests

**Root cause:** Earlier conceptual discussions included BMP/Kolari-Pynnönen-style tests even though v0.1 was subsequently narrowed to one security/event.

**Downstream consequence:** Implementing those methods in v0.1 would confuse single-firm inference with cross-sectional event-study inference.

**Minimal fix:** Cross-sectional procedures are excluded from v0.1 and reserved for the multi-event version.

**Status:** RESOLVED.

## 44.2 Placebo statistic previously called a p-value

**Root cause:** A pseudo-event-date tail frequency resembles a randomization p-value numerically but does not automatically possess the same inferential interpretation.

**Downstream consequence:** Calling it a p-value could overstate statistical validity under nonstationarity, volatility regimes, serial dependence, or unknown historical confounders.

**Minimal fix:** v0.1 calls it the **Historical Placebo Tail Proportion**. Formal nonparametric inference is separately supplied through the single-firm permutation procedure.

**Status:** RESOLVED.

## 44.3 Permutation tests described as assumption-free

**Root cause:** "Nonparametric" is sometimes incorrectly equated with "no assumptions."

**Downstream consequence:** Users could incorrectly believe permutation inference remains exact under arbitrary serial dependence or heteroskedasticity.

**Minimal fix:** The exchangeability/i.i.d. requirement is explicitly disclosed, and dependence/variance diagnostics can generate warnings.

**Status:** RESOLVED.

## 44.4 Automatic detection of confounding announcements

**Root cause:** The proposed app has no external news/event database in v0.1.

**Downstream consequence:** Claiming to have ruled out confounders would be false.

**Minimal fix:** Confounder status is `NOT ASSESSABLE` unless information is supplied.

**Status:** RESOLVED.

## 44.5 Automatic trading-date shifting

**Root cause:** Calendar dates do not reveal whether information arrived before, during, or after trading.

**Downstream consequence:** Silent alignment can assign the price response to the wrong event day.

**Minimal fix:** EFL may suggest but cannot silently determine the effective event trading date; user confirmation is required and recorded.

**Status:** RESOLVED.

## 44.6 Robustness analysis could become specification mining

**Root cause:** Allowing users to inspect many windows after seeing results creates scope for selective reporting.

**Downstream consequence:** A tool intended to increase credibility could inadvertently facilitate p-hacking.

**Minimal fix:** Primary and robustness specifications are locked before calculation; modifications create a new run.

**Status:** RESOLVED.

## 44.7 Arbitrary minimum estimation window presented as universal

**Root cause:** No universal minimum observation count applies to every event study.

**Downstream consequence:** A hard threshold could falsely imply methodological consensus.

**Minimal fix:** EFL's 60/120 safeguards are explicitly labeled operational platform thresholds rather than universal econometric rules.

**Status:** RESOLVED.

## 44.8 Event-induced variance

**Root cause:** A single event provides very little information from which to estimate a new event-period variance regime.

**Downstream consequence:** Attempting a sophisticated correction could create false precision.

**Minimal fix:** v0.1 detects and warns; multi-event variance-adjusted procedures remain future work.

**Status:** RESOLVED.

## 44.9 Causal language

**Root cause:** Event studies are often described informally as estimating an event's "effect."

**Downstream consequence:** Users may overinterpret abnormal performance as causal identification.

**Minimal fix:** EFL explicitly separates computation, inference, association, and causal attribution.

**Status:** RESOLVED.

## 44.10 Citation versus coercion

**Root cause:** The project seeks scholarly credit while remaining free and open source.

**Downstream consequence:** Requiring citations as informal "payment" would weaken the project's academic ethos.

**Minimal fix:** Citation is requested when the software materially contributes to research and is facilitated through standard scholarly software infrastructure.

**Status:** RESOLVED.

# 45. Remaining Deliberately Unfrozen Decisions

These decisions should **not** be guessed before implementation planning:

1. programming language;
2. front-end framework;
3. client-side versus hybrid computation implementation;
4. exact repository directory layout;
5. exact OSI-approved license;
6. deployment provider;
7. visual design; and
8. performance optimization strategy.

These are engineering decisions.

They cannot alter the frozen methodological behavior without formally amending this specification.

# 46. Frozen v0.1 Scientific Core

The scientific core is now:

$$
\boxed{
\begin{aligned}
&\text{Single security + single event}\\
&\text{Daily short-horizon returns}\\
&\text{Market model primary}\\
&\text{Market-adjusted robustness}\\
&\text{AR + CAR}\\
&\text{Classical inference}\\
&\text{Single-firm permutation inference}\\
&\text{Historical pseudo-event placebo diagnostic}\\
&\text{Prespecified specification robustness}\\
&\text{Research-integrity audit}\\
&\text{Deterministic Referee Mode}\\
&\text{Reproducibility bundle}\\
&\text{Version-specific citation}
\end{aligned}
}
$$

# 47. Decision Gate

**The research and product specification is sufficiently internally consistent to proceed to implementation architecture.**

However, implementation is authorized only under the following rule:

> **No numerical method may enter the production engine until its mathematical specification, assumptions, expected behavior, and known-answer validation case have been documented.**

The next project stage is therefore:

## Stage II — Technical Architecture and Repository Design

Stage II must determine:

- numerical-engine architecture;
- module boundaries;
- dependency policy;
- testing architecture;
- browser/privacy architecture;
- reproducibility format;
- CI/runtime-risk framework;
- repository layout;
- contribution structure; and
- license choice.

Only after Stage II is audited should implementation code begin.

# References

Brown, S. J., & Warner, J. B. (1985). Using daily stock returns: The case of event studies. *Journal of Financial Economics, 14*(1), 3-31.

Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-study methodology under conditions of event-induced variance. *Journal of Financial Economics, 30*(2), 253-272.

Corrado, C. J. (1989). A nonparametric test for abnormal security-price performance in event studies. *Journal of Financial Economics, 23*(2), 385-395.

Kolari, J. W., & Pynnönen, S. (2010). Event study testing with cross-sectional correlation of abnormal returns. *Review of Financial Studies, 23*(11), 3996-4025.

MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature, 35*(1), 13-39.

Nguyen, B. D., & Wolf, M. (2024). Single-firm event studies and permutation inference. *Empirical Economics*. [Exact bibliographic metadata to be verified before public release.]

# End of Authoritative v0.1 Specification
