<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>STATUS: FROZEN FOR IMPLEMENTATION</strong></p>
<p>This document converts the frozen Stage I scientific specification
into an implementable architecture. It contains no production
application code. Any implementation that conflicts with Stage I
scientific rules must be rejected or formally amend Stage I before
release.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **Product**                 | Audit-First Event Study Analyzer                                                   |
|-----------------------------|------------------------------------------------------------------------------------|
| **Architecture version**    | Stage II v0.1                                                                      |
| **Date**                    | 16 August 2026                                                                     |
| **Primary execution model** | Static web application; client-side computation                                    |
| **Scientific authority**    | Stage I Authoritative Research, Methodology, Validation, and Product Specification |
| **Next gate**               | Stage III — implementation of validation corpus and numerical core                 |

*Engineering principle: methodological correctness \> determinism \>
auditability \> privacy \> performance \> interface convenience.*

# 1. Executive Architecture Decision

Stage II freezes a browser-first, research-software architecture in
which the numerical methods remain a standalone Python package and the
public web application executes that package locally inside the user’s
browser. No application server, research-data upload endpoint, database,
user account, telemetry service, advertising system, or AI inference
service is permitted in v0.1.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Frozen architecture</strong></p>
<p>TypeScript/Vite static interface → module Web Worker → Pyodide → EFL
Python core → deterministic result objects → local rendering/export. Raw
research data do not leave the browser in the v0.1 design.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **ID** | **Decision**       | **Frozen choice**                         | **Reason**                                                                      |
|--------|--------------------|-------------------------------------------|---------------------------------------------------------------------------------|
| A01    | Numerical language | Python                                    | Preserves research transparency and future package reuse.                       |
| A02    | Core dependencies  | NumPy + SciPy only                        | Minimizes numerical dependency surface; no production reliance on statsmodels.  |
| A03    | Web execution      | Pyodide in a module Web Worker            | Runs scientific Python client-side without blocking the UI.                     |
| A04    | Frontend           | Framework-free TypeScript built with Vite | Small UI dependency surface; compile-time type checking.                        |
| A05    | Hosting            | Static deployment; GitHub Pages initially | No backend is required for v0.1.                                                |
| A06    | Testing            | pytest + Vitest + Playwright              | Unit, integration, and cross-browser coverage.                                  |
| A07    | Randomness         | Explicit NumPy Generator with PCG64       | Seeded, named bit generator with stream-compatibility guarantee for fixed seed. |
| A08    | Hashing            | SHA-256                                   | Stable content fingerprints and run identity.                                   |
| A09    | License            | BSD-3-Clause                              | OSI-approved, permissive academic/open-source license.                          |
| A10    | AI use in runtime  | None                                      | Numerical and Referee Mode outputs remain deterministic and auditable.          |

# 2. Architecture Objectives and Non-Objectives

## 2.1 Objectives

- One authoritative numerical implementation used by tests, browser
  application, future command-line tooling, and future Python package
  distribution.

- No silent methodological behavior: every transformation, exclusion,
  warning, random seed, and specification choice is inspectable and
  exportable.

- Deterministic reruns under the same release, canonical input,
  specification, and RNG state.

- Browser privacy by architecture rather than by privacy-policy promise.

- Fail-fast validation before expensive permutation or placebo
  computation.

- Bounded runtime with workload estimation, cancellation, and hard caps;
  no unbounded jobs.

- Cross-runtime parity between CPython reference execution and the
  Pyodide/browser execution used by end users.

## 2.2 Non-objectives for v0.1

- No cloud database, authentication, saved user profiles, server-side
  computation, or remote file storage.

- No automatic retrieval of market data, news, CRSP, Compustat, WRDS, or
  other licensed data.

- No LLM-generated numerical analysis, causal certification, or
  open-ended narrative generation.

- No plugin system or third-party numerical model execution.

- No mobile-native application; the responsive web interface is the
  first public client.

# 3. System Context and Data Flow

The public application is a static web client. The browser receives
static application assets from the host. After that initial load,
research data are read from the user-selected local file into browser
memory and passed to the numerical Web Worker. The worker invokes the
packaged Python core through Pyodide. Only deterministic result objects
return to the interface.

USER FILE  
↓ explicit column mapping / units  
VALIDATION GATE  
↓ only if valid or explicitly acknowledged  
LOCKED ANALYSIS SPECIFICATION  
↓  
WEB WORKER + PYODIDE  
↓  
EFL PYTHON CORE  
├─ event-time engine  
├─ expected-return models  
├─ AR/CAR engine  
├─ classical inference  
├─ permutation inference  
├─ historical placebo engine  
├─ robustness engine  
└─ deterministic audit engine  
↓  
IMMUTABLE RESULT OBJECT  
↓  
UI + REFEREE MODE + REPRODUCIBILITY EXPORT

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Privacy consequence</strong></p>
<p>The v0.1 architecture must not contain fetch/XHR calls that transmit
uploaded research data, computed results, file names, or analysis
specifications to an EFL-controlled service. Third-party analytics and
telemetry are prohibited.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 4. Technology Stack

| **Layer**           | **Choice**        | **Role**                                                             | **Version policy**                                                                                                      |
|---------------------|-------------------|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Numerical core      | Python            | Authoritative calculations and audit logic                           | Exact supported minor version(s) pinned in each release; CI tests at least two maintained CPython minors when feasible. |
| Numerical libraries | NumPy, SciPy      | Linear algebra, numerical arrays, statistical distribution functions | Exact versions captured in release/environment manifest and browser runtime.                                            |
| Browser Python      | Pyodide           | Runs the same Python core inside browser WebAssembly                 | Pin a specific stable Pyodide release per EFL release; never use an unpinned latest URL.                                |
| Worker boundary     | Module Web Worker | Prevents long calculations from freezing the interface               | Worker protocol versioned with application.                                                                             |
| UI language         | TypeScript        | Typed user-interface state and worker messages                       | Strict type checking.                                                                                                   |
| Build tool          | Vite              | Static asset build and GitHub Pages deployment                       | Exact npm dependency lock committed.                                                                                    |
| Browser unit tests  | Vitest            | UI/data-contract unit tests                                          | Pinned by package lock.                                                                                                 |
| Browser E2E         | Playwright        | Cross-browser user-flow and Pyodide parity tests                     | Chromium, Firefox, WebKit release gate.                                                                                 |
| Python tests        | pytest            | Core unit/integration/golden tests                                   | Pinned CI environment.                                                                                                  |
| CI/CD               | GitHub Actions    | Automated release gates and static deployment                        | Actions pinned to stable major/reviewed revisions.                                                                      |

The current Pyodide documentation supports NumPy and SciPy in the
browser and explicitly documents Pyodide execution in a module Web
Worker. GitHub Pages is a static-site host, and Vite documents static
deployment to GitHub Pages. These capabilities make the no-backend
architecture technically viable. \[T1–T4\]

# 5. Python Package Architecture

The numerical core is a normal installable Python package. Browser
support is an adapter, not a fork. The package must contain no DOM,
browser, network, or filesystem assumptions in the calculation modules.

| **Module** | **Responsibility**                             | **May depend on**       | **Must not do**                                             |
|------------|------------------------------------------------|-------------------------|-------------------------------------------------------------|
| schema     | Typed internal records and enums               | Python standard library | Perform computation or I/O.                                 |
| validation | Input/schema/date/unit/data-integrity checks   | schema, stdlib          | Silently modify data.                                       |
| event_time | Trading-index and window construction          | schema, NumPy           | Guess unconfirmed event timing.                             |
| models     | Market model and market-adjusted model         | NumPy                   | Use event-window observations to estimate the market model. |
| abnormal   | Expected returns, AR, CAR                      | NumPy, models           | Impute event-window returns.                                |
| inference  | Classical and permutation inference            | NumPy, SciPy            | Use global RNG state.                                       |
| placebo    | Admissible pseudo-events and tail distribution | NumPy, models, abnormal | Relabel placebo tail proportion as causal p-value.          |
| robustness | Prespecified model/window matrix               | Core modules            | Search for the most significant specification.              |
| audit      | PASS/WARNING/CRITICAL/NOT ASSESSABLE rules     | Results + validation    | Use unconstrained AI judgment.                              |
| reporting  | Canonical result/export objects                | All result modules      | Recompute numerical results.                                |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>One-source-of-truth rule</strong></p>
<p>All UI-visible numerical values must originate from the Python core
result object. TypeScript may format, sort, filter, or visualize
results, but must not independently recompute econometric
quantities.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 6. Core Dependency Policy

- Production numerical core: Python standard library + NumPy + SciPy
  only unless a future methodology amendment demonstrates a clear need.

- No statsmodels dependency in v0.1 production logic. Independent
  statsmodels/R implementations may be used only as validation
  comparators.

- No dependency may be added merely to implement a few lines of
  deterministic logic that can be transparently maintained in-core.

- Every dependency addition requires: purpose, license check,
  browser/Pyodide compatibility check, security review, and
  numerical-impact classification.

- Python packaging metadata lives in pyproject.toml, consistent with
  current Python packaging guidance. \[T5\]

- Frontend dependencies are committed with an npm lockfile. Automated
  dependency-security review is enabled where GitHub plan/repository
  support permits. \[T6\]

# 7. Canonical Input Pipeline

The input pipeline is deliberately staged. Validation produces an
immutable candidate dataset; user-acknowledged normalizations produce a
new canonical dataset. Calculation cannot mutate either.

| **Stage**       | **Action**                                                                     | **Result**          |
|-----------------|--------------------------------------------------------------------------------|---------------------|
| Raw intake      | Read local file bytes; compute raw-file SHA-256; do not transmit               | RawFileRecord       |
| Parse           | Decode CSV; map user-selected columns; preserve source row number              | ParsedRows          |
| Validate        | Dates, numeric finiteness, units, duplicates, missingness, return bounds       | ValidationReport    |
| User resolution | Explicitly approve permissible actions such as ascending date sort             | NormalizationRecord |
| Canonicalize    | Convert dates to ISO trading dates; returns to decimal float64; lock row order | CanonicalDataset    |
| Fingerprint     | Hash canonical row serialization                                               | CanonicalDataHash   |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>No silent sorting</strong></p>
<p>An unsorted input file may be offered an explicit “sort ascending by
date” action. The user must approve it. The action and pre/post
fingerprints are recorded. Duplicate dates remain CRITICAL and cannot be
automatically resolved.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 8. Canonical Data Representation

- Date: ISO calendar date (YYYY-MM-DD) mapped to an integer trading
  index after validation.

- Returns: IEEE-754 binary64 values internally, always in decimal units.

- Missing: explicit missing marker before validation; no missing value
  is represented as numeric zero.

- Row provenance: each canonical observation retains the original source
  row index for audit reporting.

- Ordering: strictly ascending date after explicit
  validation/normalization.

For hashing, canonical values are serialized deterministically rather
than relying on locale-sensitive or display-formatted strings. The
raw-file hash and canonical-data hash are both exported so that users
can distinguish byte-identical inputs from analytically identical
normalized data.

# 9. Analysis Specification Contract

Before calculation, the interface creates a locked AnalysisSpecification
record. It is immutable for that run. Any material edit creates a new
specification hash and new run identity.

| **Required field group** | **Examples**                                                                        |
|--------------------------|-------------------------------------------------------------------------------------|
| Event identity           | calendar announcement date; confirmed effective trading date; timing-known flag     |
| Data semantics           | return-unit declaration; benchmark label; optional source metadata                  |
| Primary design           | expected-return model; estimation start/end; event start/end; contamination gap     |
| Robustness design        | up to three prespecified secondary windows; alternative model flag                  |
| Inference                | two-sided default or explicitly prespecified one-sided; permutation count; RNG seed |
| Placebo                  | enabled flag; user-supplied excluded/confounding periods                            |
| Normalization            | explicit transformations approved before lock                                       |

# 10. Run Identity and Cryptographic Fingerprints

EFL uses SHA-256 content fingerprints for reproducibility and change
detection. SHA-256 is specified by NIST’s Secure Hash Standard. \[T7\]

| **Identifier**    | **Definition**                                                                          | **Purpose**                                       |
|-------------------|-----------------------------------------------------------------------------------------|---------------------------------------------------|
| RawFileHash       | SHA-256 of uploaded file bytes                                                          | Detect byte-for-byte source changes.              |
| CanonicalDataHash | SHA-256 of deterministic canonical dataset serialization                                | Identify analytically used data.                  |
| SpecHash          | SHA-256 of canonical AnalysisSpecification serialization                                | Identify methodological configuration.            |
| AnalysisID        | SHA-256(CanonicalDataHash + SpecHash)                                                   | Stable identity of data + research specification. |
| ExecutionID       | SHA-256(AnalysisID + EFL version + core build commit + runtime manifest + RNG manifest) | Identify the exact software/runtime execution.    |

AnalysisSpecification is serialized using a documented deterministic
JSON-canonicalization procedure. RFC 8785 provides a formal JSON
Canonicalization Scheme suitable for deterministic hashing; EFL will
either conform to it or ship an equivalently specified canonicalizer
with conformance tests. \[T8\]

# 11. Randomness and Reproducibility

No production computation may use module-global random state or an
implicit default generator. All stochastic operations receive a
run-scoped RNG object.

- Generator: NumPy Generator instantiated with explicit PCG64(seed).

- Default displayed seed: deterministically generated at specification
  creation and visible/editable before lock; never silently regenerated
  during a run.

- Manifest records: bit generator name, seed, NumPy version, permutation
  count, algorithm version.

- Permutation and sampled-placebo streams are separated using
  deterministic child seeds derived from the locked run seed so one
  procedure cannot change the other merely by consuming additional
  random draws.

- PCG64 is selected because NumPy documents a compatibility guarantee
  that a fixed seed produces the same random integer stream. \[T9\]

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Important reproducibility boundary</strong></p>
<p>Exact floating-point identity across arbitrary future
NumPy/SciPy/browser versions is not promised. The exact runtime manifest
is therefore part of ExecutionID, and archived EFL releases pin their
numerical environment.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 12. Numerical Engine Contracts

## 12.1 Market-model estimation

- OLS is fit only on usable estimation-window observations.

- Design matrix contains intercept and benchmark return.

- Rank deficiency, zero benchmark variance, nonfinite estimates, or
  insufficient residual degrees of freedom produce explicit failure
  states.

- The engine returns coefficients, covariance ingredients required by
  Stage I inference, residuals, fitted values, R-squared, residual
  scale, and observation provenance.

## 12.2 AR/CAR

- Expected returns are computed from the locked model specification.

- Event-window AR is a length-preserving vector keyed to event-time
  index.

- CAR is reported only when every required event-window observation is
  valid.

- Intermediate precision is binary64; UI rounding occurs only at
  presentation time.

## 12.3 Inference

- Classical inference and permutation inference return separate result
  objects and separate assumptions.

- Permutation test uses only the run-scoped RNG and the Stage I default
  B=20,000 unless the locked user specification selects another
  supported value.

- Supported v0.1 Monte Carlo permutation range: 1,000–100,000; interface
  warns below 10,000; default remains 20,000.

- No p-value is silently rounded to 0.000; very small values are
  formatted with an inequality while retaining full machine value in
  exports.

# 13. Historical Placebo Engine

The placebo engine first enumerates admissible candidate dates from the
canonical trading calendar using Stage I rules. Candidate generation is
deterministic. Model fitting and CAR calculation then reuse the same
core functions used by the actual event; there is no separate “placebo
math.”

- All admissible pseudo-events are used when candidate count is within
  v0.1 workload caps.

- If future sampling becomes necessary, it must use a separate
  deterministic RNG stream and must disclose candidate count, requested
  sample, realized sample, and seed.

- Actual-event exclusion regions and user-supplied confounding/exclusion
  dates are applied before candidate calculation.

- Every placebo result retains pseudo-event date and candidate-exclusion
  reason codes for auditability.

- The reported quantity remains Historical Placebo Tail Proportion,
  never a causal p-value.

# 14. Audit Engine Architecture

Audit logic is deterministic and rule-addressable. Every rule has a
stable rule ID, stage, status mapping, machine-readable evidence,
human-readable explanation, and Stage I specification reference.

| **Rule family** | **Example stable IDs**                                          | **Execution point**     |
|-----------------|-----------------------------------------------------------------|-------------------------|
| Input           | DATA_DUPLICATE_DATE, DATA_INVALID_RETURN, DATA_UNIT_UNCONFIRMED | Before lock/calculation |
| Event           | EVENT_ALIGNMENT_UNCERTAIN, EVENT_WINDOW_INCOMPLETE              | Before AR/CAR           |
| Estimation      | EST_SHORT_HISTORY, EST_RANK_DEFICIENT                           | Before/after model fit  |
| Inference       | INF_SERIAL_DEPENDENCE_WARNING, INF_VARIANCE_WARNING             | After model diagnostics |
| Placebo         | PLC_NO_ADMISSIBLE_DATES, PLC_LOW_CANDIDATE_COUNT                | Before/after placebo    |
| Interpretation  | INT_CONFOUNDERS_NOT_ASSESSABLE, INT_CAUSAL_NOT_ESTABLISHED      | Reporting stage         |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Audit invariance</strong></p>
<p>Referee Mode cannot promote or demote a rule. It summarizes the audit
state. If the rule engine says CRITICAL, the narrative must preserve
that status.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 15. Referee Mode Architecture

- No LLM or probabilistic text generator in v0.1.

- Narrative sentences are selected from version-controlled templates
  keyed to stable audit/result states.

- Each displayed paragraph can be traced to the rule/result IDs that
  generated it.

- Template changes are classified as reporting-only unless they alter
  substantive interpretation language.

- Referee Mode must include “not assessable” statements rather than
  converting missing external evidence into reassurance.

# 16. Frontend State Machine

The interface follows a strict state machine to prevent stale or mixed
results.

| **State**        | **Permitted transition**        | **Invariant**                                       |
|------------------|---------------------------------|-----------------------------------------------------|
| EMPTY            | → FILE_LOADED                   | No analysis results exist.                          |
| FILE_LOADED      | → VALIDATED or ERROR            | Raw file hash fixed.                                |
| VALIDATED        | → SPEC_DRAFT                    | Critical data problems resolved.                    |
| SPEC_DRAFT       | → SPEC_LOCKED                   | No numerical results yet.                           |
| SPEC_LOCKED      | → RUNNING                       | SpecHash fixed.                                     |
| RUNNING          | → COMPLETE / FAILED / CANCELLED | Previous results hidden and inaccessible to export. |
| COMPLETE         | → NEW_SPEC or EXPORT            | Displayed results match current ExecutionID.        |
| FAILED/CANCELLED | → SPEC_DRAFT / RETRY            | No partial result is labeled complete.              |

# 17. Worker Protocol

The TypeScript interface and Python worker communicate through versioned
message envelopes. Messages contain structured data only; no arbitrary
Python source supplied by users is executed.

| **Direction** | **Message class** | **Contents**                                                       |
|---------------|-------------------|--------------------------------------------------------------------|
| UI → worker   | INIT              | Expected EFL core version; worker protocol version.                |
| UI → worker   | VALIDATE          | Parsed/canonical candidate data + declared units.                  |
| UI → worker   | RUN               | Locked specification + canonical data + fingerprints.              |
| UI → worker   | CANCEL            | ExecutionID or pending job token.                                  |
| worker → UI   | PROGRESS          | Named phase + bounded percentage; never fabricated time remaining. |
| worker → UI   | RESULT            | Immutable result schema + ExecutionID.                             |
| worker → UI   | ERROR             | Stable error code + safe diagnostic details.                       |

# 18. Runtime-Risk Controls

Runtime safety is a release requirement, not an optimization
afterthought. A browser research tool must never begin an effectively
unbounded computation.

| **Risk**                       | **Preventive control**                                                       | **Failure behavior**                                                 |
|--------------------------------|------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Malformed/huge input           | Schema checks; v0.1 hard cap 25,000 rows                                     | Reject before worker calculation.                                    |
| Excessive permutation workload | B limited to 100,000; estimate workload before start                         | Reject unsupported B or require lower value.                         |
| UI freeze                      | All Python computation in Web Worker                                         | Main UI remains responsive; cancel remains available.                |
| Unbounded run                  | Per-run watchdog; 45-second hard computation budget in public v0.1           | Terminate worker job; return COMPUTATION_TIMEOUT; no partial result. |
| Stale result                   | Execution-token/state checks                                                 | Discard late result from superseded job.                             |
| Worker crash                   | Worker lifecycle isolation                                                   | FAILED state; no prior result reuse.                                 |
| Nonfinite numerical result     | Finite-number assertions at module boundaries                                | NUMERICAL_NONFINITE CRITICAL failure.                                |
| Memory growth                  | Fresh worker reset after completed/cancelled heavy run if threshold exceeded | Clear worker state; preserve only exported result object.            |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Bounded-work rule</strong></p>
<p>No public v0.1 operation is allowed to run for minutes or hours. If a
methodological extension cannot satisfy the workload budget, it belongs
in a later architecture rather than being hidden behind a
spinner.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 19. Performance Budgets

These are engineering release budgets, not claims about every device.
They are evaluated on a documented reference desktop environment and
reported transparently.

| **Workload**                               | **Release target**                                  | **Hard behavior**                                            |
|--------------------------------------------|-----------------------------------------------------|--------------------------------------------------------------|
| Load + validate 10,000 rows                | ≤ 1 second median after Pyodide/core initialization | No hard fail if slower; profile regression if \>2× baseline. |
| Primary market-model + AR/CAR              | ≤ 0.5 second median                                 | Must remain interactive.                                     |
| 20,000-permutation test                    | ≤ 5 seconds median                                  | Subject to 45-second watchdog.                               |
| Historical placebo on 10,000-row history   | ≤ 5 seconds median                                  | Subject to 45-second watchdog.                               |
| Full default run after warm initialization | ≤ 10 seconds median                                 | Release blocked by material unexplained regression.          |

Cold-start Pyodide download/initialization time is measured separately
from computation because it depends materially on network/cache
conditions. The interface must distinguish “loading analysis engine”
from “running analysis.”

# 20. Numerical Tolerance Policy

Tests distinguish mathematical equality, floating-point parity, and
presentation equality.

| **Class**                         | **Default acceptance**                                                                                    |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------|
| Exact structural outputs          | Exact equality: dates, window membership, counts, statuses, rule IDs, hashes.                             |
| Core continuous quantities        | absolute tolerance 1e-12 plus relative tolerance 1e-10 unless a fixture documents a stronger requirement. |
| Distribution/p-value calculations | absolute tolerance 1e-10 against independent reference.                                                   |
| Displayed rounded values          | Must be derived from unrounded stored values; presentation tests compare declared rounding rule.          |
| Permutation outputs               | Same pinned environment + same seed must reproduce identical selected permutations and p-value.           |

# 21. Authoritative Validation Corpus

The validation corpus is created before production implementation and
committed as small, human-inspectable fixtures with expected outputs
computed independently.

| **Fixture ID** | **Purpose**                               | **Expected invariant**                                         |
|----------------|-------------------------------------------|----------------------------------------------------------------|
| KA-001         | Exact zero-abnormal-return synthetic case | All event AR and CAR exactly zero within tolerance.            |
| KA-002         | Known +5% event shock                     | AR(0)=0.05 and target CAR reflects injected shock.             |
| KA-003         | Known multi-day shock                     | AR(-1)=.01, AR(0)=.03, AR(+1)=-.01; CAR\[-1,+1\]=.03.          |
| KA-004         | Known alpha/beta market model             | Estimated coefficients match independent analytical solution.  |
| KA-005         | Market-adjusted restriction               | AR equals security minus benchmark for every valid event date. |
| INF-001        | Classical inference reference             | Statistic and two-sided p-value match independent reference.   |
| INF-002        | Seeded permutation reference              | Same fixed seed/B reproduces expected permutation result.      |
| PLC-001        | Hand-enumerable placebo history           | Admissible dates and tail proportion match manual calculation. |
| ROB-001        | Two-model robustness matrix               | Rows, signs, magnitudes, and inference flags match fixtures.   |

# 22. Failure-Mode Corpus

| **Fixture** | **Defect**                           | **Required response**                                                               |
|-------------|--------------------------------------|-------------------------------------------------------------------------------------|
| FM-001      | Duplicate date                       | CRITICAL; calculation blocked.                                                      |
| FM-002      | Unsorted dates                       | Explicit resolution required; no silent sort.                                       |
| FM-003      | Weekend/holiday calendar event       | Effective trading-date confirmation required.                                       |
| FM-004      | Missing event-day security return    | CRITICAL EVENT_WINDOW_INCOMPLETE.                                                   |
| FM-005      | Missing event benchmark return       | CRITICAL EVENT_WINDOW_INCOMPLETE.                                                   |
| FM-006      | Insufficient estimation history      | Stage I threshold status; research-grade classification withheld below 60.          |
| FM-007      | Overlapping estimation/event windows | CRITICAL; calculation blocked.                                                      |
| FM-008      | Return \< -100%                      | CRITICAL invalid simple return.                                                     |
| FM-009      | Ambiguous units                      | Analysis cannot lock until units explicitly declared.                               |
| FM-010      | Extreme positive return              | Preserved; outlier warning only.                                                    |
| FM-011      | Zero benchmark variance              | Model estimation failure; market model blocked.                                     |
| FM-012      | No admissible placebo date           | Placebo NOT ASSESSABLE/diagnostic unavailable; main valid result remains available. |
| FM-013      | Changed spec after result            | New SpecHash/AnalysisID; prior result retained as prior run only.                   |
| FM-014      | Worker timeout                       | FAILED COMPUTATION_TIMEOUT; no partial result.                                      |
| FM-015      | Worker returns stale ExecutionID     | Result discarded.                                                                   |

# 23. Metamorphic and Invariance Tests

- Row-order invariance after an explicitly approved ascending-date
  normalization: equivalent canonical data produce identical analytical
  output.

- Unit invariance: a decimal-return file and a numerically equivalent
  percent-return file produce identical canonical returns and results
  after correct unit declaration.

- Display-precision invariance: changing UI decimal places cannot change
  stored estimates, p-values, audit states, or exported raw values.

- Unused metadata invariance: changing a non-analytical label cannot
  change numerical results, though execution metadata may differ where
  intentionally included.

- Robustness isolation: enabling an additional prespecified robustness
  window cannot alter the primary-model primary-window result.

- RNG isolation: adding placebo computation cannot alter permutation
  results because separate deterministic streams are used.

# 24. Cross-Runtime Parity

A critical release gate is that the same EFL core produces materially
identical results under reference CPython and the pinned Pyodide browser
environment.

- Every known-answer fixture runs under CPython CI.

- A representative subset including market-model, inference,
  permutation, placebo, and audit cases runs inside Pyodide through
  Playwright.

- Continuous quantities must satisfy the tolerance policy; structural
  outputs and audit states must be identical.

- Any parity failure is a release blocker until explained and
  documented.

- Playwright is selected because it supports Chromium, Firefox, and
  WebKit, allowing the real browser application to be exercised across
  major browser engines. \[T10\]

# 25. Test Pyramid and Coverage Gates

| **Layer**                 | **Tool**                                     | **What it proves**                                 | **Release gate**                                                      |
|---------------------------|----------------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------|
| Python unit               | pytest                                       | Module math, validation, rule mapping              | 100% of scientific public functions exercised; no known failing test. |
| Python golden/integration | pytest                                       | End-to-end canonical fixtures                      | All authoritative fixtures pass.                                      |
| TypeScript unit           | Vitest                                       | State machine, formatting, message/schema handling | All pass.                                                             |
| Browser integration       | Playwright                                   | Upload→lock→run→audit→export flows                 | Chromium/Firefox/WebKit core path passes.                             |
| Cross-runtime parity      | pytest + Playwright/Pyodide                  | Browser engine matches reference core              | All parity fixtures pass within policy.                               |
| Visual smoke              | Playwright screenshots/manual release review | No clipped or inaccessible critical output         | Release checklist pass.                                               |

# 26. Continuous Integration / Release Pipeline

GitHub Actions is the CI/CD platform. GitHub’s official guidance
supports Python build/test workflows and static Pages deployment.
\[T11–T12\]

- Pull request: metadata/license checks → Python lint/type/static checks
  → pytest unit/golden tests → frontend type/unit tests → production
  build → browser E2E/parity smoke.

- Main branch: full browser matrix + dependency/security review +
  reproducibility fixtures + artifact build.

- Release tag: rerun full gates from clean checkout; generate version
  manifest; validate CITATION.cff; build static site; archive release;
  deploy only from the tested artifact.

- Deployment must never run from an untested working directory or
  manually edited generated site.

- Main branch is protected: no direct production release that bypasses
  CI.

# 27. Supply-Chain and Dependency Security

- Commit dependency lockfiles and review dependency changes in pull
  requests.

- Enable Dependabot/security updates and dependency review where
  repository features permit; GitHub documents these mechanisms for
  identifying dependency changes and known vulnerabilities. \[T6\]

- No automatic merge of dependency upgrades that touch numerical
  libraries or Pyodide; those require parity and known-answer review.

- Pin Pyodide release URL and verify integrity of deployed assets; do
  not load “latest.”

- No runtime code loaded from arbitrary user URLs.

- No secrets are required for normal application execution because the
  public app has no backend.

# 28. Privacy and Local-Data Policy

| **Category**   | **v0.1 rule**                                                                                            |
|----------------|----------------------------------------------------------------------------------------------------------|
| Research data  | Held in browser memory only during active session unless user explicitly downloads an export.            |
| File upload    | Local file picker; “upload” in UI language must not imply server transmission. Prefer “Open local file.” |
| Persistence    | No IndexedDB/localStorage persistence of research data by default.                                       |
| Telemetry      | None.                                                                                                    |
| Analytics      | None.                                                                                                    |
| Cookies        | No application cookies. Hosting platform behavior must be documented separately if applicable.           |
| Crash reports  | No automatic remote crash reporting.                                                                     |
| External links | Documentation links may navigate externally but may not carry research data in query parameters.         |

# 29. Reproducibility Bundle Format

A completed run exports a single human- and machine-readable bundle. The
archive packaging mechanism is an implementation detail; the internal
files and schemas are frozen here.

efl-run-\<short-execution-id\>/  
manifest.json  
analysis_spec.json  
data_audit.json  
model_results.json  
event_time.csv  
inference.json  
robustness.csv  
placebo_summary.json  
placebo_events.csv  
audit_report.json  
referee_report.md  
environment.json  
citation.txt  
README.txt

- Raw proprietary input data are NOT included automatically.

- manifest.json records RawFileHash and CanonicalDataHash so the
  researcher can verify the source independently.

- environment.json records EFL version, Git commit, Python, NumPy,
  SciPy, Pyodide, browser worker protocol, RNG algorithm, and relevant
  build metadata.

- CSV exports use explicit UTF-8 encoding, ISO dates, decimal returns,
  and stable column order documented in the schema.

# 30. Repository Architecture

empirical-finance-lab/  
├─ src/efl_core/  
│ ├─ schema/  
│ ├─ validation/  
│ ├─ event_time/  
│ ├─ models/  
│ ├─ abnormal/  
│ ├─ inference/  
│ ├─ placebo/  
│ ├─ robustness/  
│ ├─ audit/  
│ └─ reporting/  
├─ tests/  
│ ├─ unit/  
│ ├─ known_answer/  
│ ├─ failure_modes/  
│ ├─ invariance/  
│ └─ reference_outputs/  
├─ web/  
│ ├─ src/  
│ ├─ worker/  
│ └─ tests/  
├─ docs/  
│ ├─ methodology/  
│ ├─ diagnostics/  
│ ├─ reproducibility/  
│ └─ development/  
├─ examples/  
├─ schemas/  
├─ .github/  
│ ├─ workflows/  
│ └─ ISSUE_TEMPLATE/  
├─ pyproject.toml  
├─ package.json  
├─ package-lock.json  
├─ CITATION.cff  
├─ LICENSE  
├─ CHANGELOG.md  
├─ CONTRIBUTING.md  
├─ SECURITY.md  
└─ README.md

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Repository rule</strong></p>
<p>No generated build artifacts, user data, proprietary sample data,
credentials, or local environment files are committed to the
repository.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 31. Documentation Architecture

- README: what EFL is, what v0.1 does, quick start, privacy statement,
  citation, limitations.

- Methodology: exact Stage I equations/rules translated into user-facing
  documentation with references.

- Diagnostics catalog: every audit rule ID, trigger, severity,
  interpretation, and remedy.

- Reproducibility: hashes, run IDs, seeds, bundle format, environment
  capture.

- Validation evidence: known-answer cases and parity summaries,
  including how reference values were obtained.

- Changelog: user-visible, with explicit “numerical output impact”
  classification.

- Security: vulnerability reporting path and statement that
  sensitive/proprietary datasets should not be attached to public GitHub
  issues.

# 32. Versioning and Numerical-Impact Classification

| **Change class** | **Examples**                                                       | **Required release treatment**                                                                 |
|------------------|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| REPORTING_ONLY   | Wording, layout, documentation typo                                | Normal version increment; note no numerical impact.                                            |
| DIAGNOSTIC       | Audit threshold/message changes without numerical estimator change | Release notes identify changed rules; revalidate fixture statuses.                             |
| NUMERICAL_BUGFIX | Correction to calculation or inference                             | Mandatory highlighted disclosure; regenerated golden outputs; users warned results may change. |
| METHODOLOGY      | New estimator/test or changed scientific rule                      | Requires Stage I amendment, validation expansion, and explicit methodology release note.       |
| RUNTIME          | Pyodide/NumPy/SciPy/browser engine change                          | Cross-runtime parity and reproducibility review required.                                      |

# 33. Open-Source License and Citation

Stage II freezes BSD-3-Clause as the intended software license. The Open
Source Initiative lists BSD-3-Clause as an approved permissive license
permitting redistribution and modification under its stated conditions.
\[T13\]

Citation is encouraged through scholarly metadata rather than imposed as
a software-use fee. CITATION.cff is a human- and machine-readable
software citation format, and the repository will validate it in CI.
\[T14\]

- LICENSE: BSD-3-Clause.

- CITATION.cff: project title, author(s), version, release date,
  repository, DOI once available, ORCID when supplied.

- Formal release: GitHub Release + archived DOI record when Zenodo
  integration is enabled.

- Documentation language: “If Empirical Finance Lab materially
  contributes to your research, please cite the software using the
  version-specific citation.”

# 34. Contribution and Governance Rules

- Scientific-method changes require an issue labeled methodology-impact
  before implementation.

- No pull request may change a numerical function and its expected
  fixture output simultaneously without an independent justification
  explaining why the expected answer changed.

- Golden/reference outputs are treated as protected scientific
  artifacts: changes require review against an independent calculation.

- Audit rules require stable IDs; IDs are never silently reused for a
  different concept.

- Breaking exported-schema changes require schema-version increment and
  migration note.

- External contributors receive normal authorship/contributor credit
  appropriate to their contribution; software citation metadata follows
  scholarly contribution practice rather than automatically listing
  every code contributor as a paper author.

# 35. Error Taxonomy

| **Prefix** | **Meaning**               | **Example**             |
|------------|---------------------------|-------------------------|
| DATA\_     | Input/data contract       | DATA_DUPLICATE_DATE     |
| EVENT\_    | Event timing/window       | EVENT_WINDOW_INCOMPLETE |
| EST\_      | Estimation/model fit      | EST_RANK_DEFICIENT      |
| INF\_      | Statistical inference     | INF_INVALID_DF          |
| PLC\_      | Placebo engine            | PLC_NO_ADMISSIBLE_DATES |
| ROB\_      | Robustness engine         | ROB_SPEC_INVALID        |
| NUM\_      | Generic numerical failure | NUM_NONFINITE           |
| RUN\_      | Worker/runtime lifecycle  | RUN_TIMEOUT             |
| EXP\_      | Export/reproducibility    | EXP_SCHEMA_FAILURE      |

User-facing errors must state: what failed, why the result is
unavailable or weakened, and the minimal corrective action. Internal
stack traces are not shown as the primary message.

# 36. Accessibility and Interface Integrity

- Critical methodological status cannot be communicated by color alone;
  text labels PASS/WARNING/CRITICAL/NOT ASSESSABLE are mandatory.

- Keyboard navigation and semantic form labels are release requirements.

- Charts must have tabular equivalents and textual summaries.

- Error focus moves to the relevant input/section without destroying the
  user’s draft specification.

- Export and citation controls remain available without requiring an
  account.

# 37. Browser Support Policy

- Officially supported v0.1 desktop engines: current stable
  Chromium-family browser, Firefox, and Safari/WebKit generation covered
  by the pinned Playwright release.

- Cross-browser scientific parity is tested, not assumed.

- Unsupported browsers receive an explicit compatibility message before
  analysis rather than failing deep in Pyodide initialization.

- Mobile browsers may be usable responsively but are not part of the
  v0.1 scientific release gate.

# 38. Stage III Implementation Order

Implementation must proceed in dependency order. The UI is deliberately
late.

1.  Create repository skeleton, license, packaging metadata, CI
    skeleton, and scientific schema documents.

2.  Create authoritative validation/failure fixtures and independent
    expected-output records.

3.  Implement schema + validation only; pass validation corpus.

4.  Implement event-time + model + AR/CAR core; pass known-answer cases.

5.  Implement classical inference; validate independently.

6.  Implement deterministic RNG abstraction + permutation inference;
    lock reference fixture.

7.  Implement placebo engine; validate candidate selection and tail
    proportion manually.

8.  Implement robustness + audit + Referee Mode deterministic templates.

9.  Implement reproducibility hashes/IDs/export schemas.

10. Package core wheel and run Pyodide parity tests.

11. Only then implement full user-facing interface and visualization.

12. Run complete runtime-risk, browser, privacy, and release audit
    before public deployment.

# 39. Stage II Acceptance Criteria

| **Gate**                   | **Requirement**                                                                                                           | **Status**       |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------|------------------|
| Architecture consistency   | Every Stage I scientific requirement has a clear implementation owner/module or explicit non-applicable v0.1 disposition. | PASS — specified |
| Single numerical authority | No duplicated JavaScript econometric implementation is planned.                                                           | PASS — specified |
| Privacy                    | No backend/data upload/telemetry dependency is required for normal v0.1 operation.                                        | PASS — specified |
| Determinism                | RNG, hashing, versions, and run identity are explicitly specified.                                                        | PASS — specified |
| Runtime safety             | Input/B caps, worker isolation, cancellation, stale-result protection, and watchdog behavior are specified.               | PASS — specified |
| Validation                 | Known-answer, failure-mode, invariance, and cross-runtime parity suites are specified before implementation.              | PASS — specified |
| Release governance         | CI, dependency security, versioning, and numerical-impact classification are specified.                                   | PASS — specified |
| Scholarly infrastructure   | BSD-3-Clause, CITATION.cff, versioning, and DOI-ready release structure are specified.                                    | PASS — specified |

# 40. Internal Consistency Audit of Stage II

| **Issue**                                     | **Root cause**                                                                                | **Minimal architectural fix**                                                                             | **Status** |
|-----------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|------------|
| I01 — Browser privacy vs Python reuse         | A serverless browser design could have forced a separate JavaScript numerical implementation. | Using Pyodide preserves the same Python core in-browser; TypeScript cannot recompute econometric results. | RESOLVED   |
| I02 — Long computations vs responsive UI      | Permutation/placebo work can block the main browser thread.                                   | All numerical work executes in a module Web Worker with cancel/watchdog controls.                         | RESOLVED   |
| I03 — Reproducibility vs changing default RNG | Using default_rng without naming the algorithm can change future streams.                     | Explicit PCG64(seed), algorithm/version manifest, and separated streams are frozen.                       | RESOLVED   |
| I04 — “Same run” ambiguity                    | Data/spec/software changes were previously conflated.                                         | Separate RawFileHash, CanonicalDataHash, SpecHash, AnalysisID, and ExecutionID.                           | RESOLVED   |
| I05 — Privacy claim vs third-party analytics  | Even a static site could leak data through analytics or telemetry.                            | No analytics, telemetry, research-data network calls, or remote crash reporting in v0.1.                  | RESOLVED   |
| I06 — Golden tests self-confirming bugs       | Updating implementation and expected answer together could hide an error.                     | Golden-output changes require independent calculation/justification.                                      | RESOLVED   |
| I07 — Placebo math drifting from event math   | Separate implementations could produce inconsistent definitions.                              | Placebo engine reuses the same model/AR/CAR functions.                                                    | RESOLVED   |
| I08 — Stale results after failed rerun        | A UI could accidentally show a previous successful result.                                    | Strict state machine + ExecutionID validation + stale-result discard.                                     | RESOLVED   |
| I09 — Open source vs citation goal            | A restrictive “citation required” license would conflict with open-source norms.              | BSD-3-Clause for software rights; citation requested through CITATION.cff/DOI scholarly practice.         | RESOLVED   |
| I10 — Runtime expectations                    | A research tool could become unbounded as features accumulate.                                | Hard public caps and 45-second watchdog; expensive future methods require new architecture.               | RESOLVED   |

# 41. Remaining Release-Pin Decisions (Not Architecture Gaps)

The following are intentionally pinned at the Stage III/release commit
because freezing today’s version numbers would age the document without
improving architecture correctness:

- exact CPython minor-version test matrix;

- exact NumPy, SciPy, pytest, Pyodide, TypeScript, Vite, Vitest, and
  Playwright versions;

- exact GitHub Actions action revisions;

- exact browser versions in the release evidence report.

Each formal EFL release must nevertheless capture those exact versions
in its environment/release manifest, dependency locks, and archived
source.

# 42. Decision Gate

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>STAGE II DECISION: PASS</strong></p>
<p>The technical architecture is sufficiently specified to begin Stage
III without writing interface-first or methodologically duplicated code.
The next deliverable is the repository skeleton plus authoritative
validation corpus and reference-output manifest; production numerical
implementation begins only after those fixtures exist.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

The Stage III implementation gate remains subordinate to Stage I: if
implementation reveals a genuine methodological ambiguity, coding stops
at that boundary and the scientific specification is amended explicitly
rather than resolved silently in code.

# 43. Technical Authority References

| **ID**  | **Authority**                                                                                           | **URL**                                                                                                                       |
|---------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| \[T1\]  | Pyodide — official documentation: scientific Python packages in the browser, including NumPy and SciPy. | https://pyodide.org/en/stable/                                                                                                |
| \[T2\]  | Pyodide — Using Pyodide in a Web Worker.                                                                | https://pyodide.org/en/stable/usage/webworker.html                                                                            |
| \[T3\]  | GitHub Docs — What is GitHub Pages?                                                                     | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages                                       |
| \[T4\]  | Vite — Deploying a Static Site, including GitHub Pages.                                                 | https://vite.dev/guide/static-deploy                                                                                          |
| \[T5\]  | Python Packaging User Guide — Writing pyproject.toml.                                                   | https://packaging.python.org/en/latest/guides/writing-pyproject-toml/                                                         |
| \[T6\]  | GitHub Docs — Dependency review / Dependabot security updates.                                          | https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review  |
| \[T7\]  | NIST FIPS 180-4 — Secure Hash Standard (SHA-256).                                                       | https://csrc.nist.gov/pubs/fips/180-4/upd1/final                                                                              |
| \[T8\]  | RFC 8785 — JSON Canonicalization Scheme (JCS).                                                          | https://datatracker.ietf.org/doc/rfc8785/                                                                                     |
| \[T9\]  | NumPy — PCG64 documentation and compatibility guarantee.                                                | https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html                                                       |
| \[T10\] | Playwright — official browser-testing documentation.                                                    | https://playwright.dev/docs/browsers                                                                                          |
| \[T11\] | GitHub Docs — Building and testing Python with GitHub Actions.                                          | https://docs.github.com/actions/guides/building-and-testing-python                                                            |
| \[T12\] | GitHub Docs — Configuring a publishing source for GitHub Pages.                                         | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site |
| \[T13\] | Open Source Initiative — BSD 3-Clause License.                                                          | https://opensource.org/license/bsd-3-clause                                                                                   |
| \[T14\] | Citation File Format — official CFF documentation.                                                      | https://citation-file-format.github.io/                                                                                       |
| \[T15\] | pytest — official documentation.                                                                        | https://docs.pytest.org/en/stable/                                                                                            |

References in this Stage II document support engineering choices only.
Stage I remains the authority for econometric methodology and scientific
interpretation.
