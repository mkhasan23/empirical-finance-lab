# Contributing

Empirical Finance Lab treats scientific changes differently from ordinary software changes.

1. **Reporting-only:** wording/layout with no numerical or interpretive effect.
2. **Diagnostic:** changes audit rules/statuses but not estimators.
3. **Numerical bugfix:** changes a calculation; must regenerate affected fixtures using an independent reference and disclose numerical impact.
4. **Methodology:** adds/changes a scientific method; requires formal specification amendment before production code.
5. **Runtime:** changes runtime/dependency behavior; requires parity and reproducibility review.

Do not change a golden expected result solely because the production implementation disagrees with it. Investigate the discrepancy first.
