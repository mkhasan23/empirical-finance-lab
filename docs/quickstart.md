# Quickstart: first audit-first event study

This walkthrough uses the repository's deterministic synthetic onboarding file. No external research dataset is required.

> **Synthetic example only.** The tutorial is not a real security, real announcement, exchange calendar, investment recommendation, or causal claim. Its purpose is to verify the EFL workflow against a known numerical result.

## 1. Open the application

Use the GitHub Pages application:

`https://mkhasan23.github.io/empirical-finance-lab/`

The application opens the CSV locally in your browser. EFL does not provide a research-data upload endpoint; the scientific analysis executes in the browser worker after the runtime is initialized.

## 2. Open the tutorial CSV

Choose:

`examples/efl_tutorial_synthetic.csv`

The three standard columns should map automatically:

- Date column → `date`
- Security-return column → `security_return`
- Benchmark-return column → `benchmark_return`
- Return units → **Decimal (0.05 = 5%)**

The intake panel should report **180 data rows** and no CRITICAL structural issue. Continue to the research specification.

## 3. Prespecify the tutorial design

Enter the following values exactly:

| Field | Tutorial value |
|---|---|
| Calendar announcement date | `2025-07-31` |
| Announcement timing | Before or during trading |
| Effective event trading date | Use the suggestion: `2025-07-31` |
| Confirm effective date | Checked |
| Expected-return model | Market model |
| Estimation start (τ) | `-140` |
| Estimation end (τ) | `-20` |
| Event start (τ) | `-1` |
| Event end (τ) | `1` |
| Hypothesis direction | Two-sided |
| Permutation count (B) | `1000` |
| PCG64 seed | `20260817` |
| Historical pseudo-event placebo | Unchecked |
| Alternative model | Unchecked |

For this minimal tutorial, clear the prefilled robustness Window 1 and Window 2 start/end fields so no secondary windows are requested. Leave exclusions blank.

Review and lock the specification before execution. The lock is methodologically material: changing the design after execution creates a new run rather than silently mutating the completed result.

## 4. Run and verify the known answer

Choose **Run locked analysis**. The primary result should be:

- State: **COMPLETE**
- Model: **market model**
- Event window: **[-1,+1]**
- AR(-1): **+1.000%**
- AR(0): **+3.000%**
- AR(+1): **-1.000%**
- CAR[-1,+1]: **+3.000%**

The Stage VII-E1 CI gate independently runs the frozen Python authority against the committed tutorial CSV/specification and enforces these numerical values. A mismatch is a release-gate failure, not something the documentation may redefine.

## 5. Read the audit before interpreting the CAR

Open **Integrity audit** and **Referee Mode**. EFL deliberately separates computation from identification. A nonzero or statistically significant CAR does not establish that the announcement caused the return; the tutorial itself is synthetic and supplies no external confounder evidence.

## 6. Export the reproducibility bundle

Open **Reproduce & cite** and download the reproducibility ZIP. The bundle records the locked specification, scientific results, audits, run identities, hashes, and build/runtime provenance while keeping the original local CSV outside the bundle by default.

Stage VII-D2 separately verifies the privacy-preserving round trip using the exact original CSV plus the exported bundle and requires deterministic re-export.

## Expected-file integrity

The committed tutorial CSV must have SHA-256:

`e3b4d1004ee960106ac17618e680f5af4fb1c5286ff5d58234bb903bc321797e`

From repository root, maintainers can verify the complete onboarding contract with:

```bash
python tools/check_stage7_e1_onboarding_gate.py
```
