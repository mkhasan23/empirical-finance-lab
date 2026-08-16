# Stage IV Operational Clarifications

**Status:** implementation clarifications that do not alter the frozen Stage I estimators or Stage III golden answers.

## D-001 — Extreme positive-return warning

Stage I requires extreme positive returns to be preserved and permits a non-destructive outlier warning, but it does not freeze a numeric threshold. Stage IV therefore uses a deliberately conservative engineering anomaly flag:

- simple return `> 2.0` (greater than +200%) → `DATA_EXTREME_RETURN` WARNING;
- the observation is never winsorized, deleted, or changed automatically.

This threshold affects only the diagnostic warning state. It does not alter any estimator, inference procedure, or reported return.

## D-002 — Historical placebo means pre-event history

The historical placebo engine restricts pseudo-event dates to dates strictly before the confirmed actual event date. This follows the project's stated purpose of asking whether comparable CARs occur in the security's own *historical/pre-event* record and avoids allowing the realized event to contaminate later pseudo-event histories.

All other Stage I placebo eligibility rules remain unchanged.

## D-003 — Referee Mode placebo label

The continuous Historical Placebo Tail Proportion is always the primary reported quantity. For the deterministic Referee Mode text only:

- tail proportion `<= 0.05` → `UNUSUAL`;
- otherwise → `NOT UNUSUAL`.

This descriptive label is not a causal p-value and does not establish causal attribution.

## D-004 — Inference-assumption diagnostics

Stage I requires explicit warnings when there is evidence of substantial serial dependence or variance instability, without freezing a diagnostic implementation. Stage IV uses:

- Ljung-Box Q(1) at 5% for lag-1 serial-dependence warning;
- Brown-Forsythe (median-centered Levene) comparison of the first and second halves of estimation residuals at 5% for estimation-period variance-instability warning.

These diagnostics do not alter AR, CAR, classical inference, or permutation inference. They only qualify interpretation of assumptions.

The event-window mean squared abnormal return divided by estimation residual variance is retained as a descriptive scale diagnostic. It is not treated as a formal event-induced-variance test because a single short event window cannot separately identify a new variance regime with useful precision.

## D-005 — Restricted canonical JSON for SpecHash

Stage II permits RFC 8785 or an equivalently specified deterministic canonicalizer. Stage IV uses sorted-key, whitespace-free UTF-8 JSON for the restricted specification domain, with non-finite numbers forbidden. All caller-supplied specification fields are preserved in the hashed representation so future material metadata cannot silently disappear from `SpecHash`.

Scientific floating-point return data are not hashed through JSON. Canonical dataset hashing uses ISO dates plus exact IEEE-754 `float.hex()` representations and an explicit `MISSING` token.
