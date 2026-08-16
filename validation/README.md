# Authoritative validation corpus

These fixtures define the Stage III ground truth for the future numerical implementation.

## Rule

**Never regenerate expected results using the production code under test.**

Every fixture stores its input, locked specification (when applicable), expected output/behavior, and SHA-256 fingerprint in `manifest.json`. Numerical tolerances follow Stage II: core continuous quantities use absolute `1e-12` plus relative `1e-10` unless a fixture explicitly states otherwise; p-value references use the fixture-declared tolerance.

## Categories

- `known_answer/`: deterministic AR/CAR/model coefficient fixtures.
- `inference/`: classical and permutation inference references.
- `placebo/`: hand-enumerable historical placebo diagnostic.
- `robustness/`: prespecified model comparison.
- `failure_modes/`: data, specification, and runtime failure contracts.
