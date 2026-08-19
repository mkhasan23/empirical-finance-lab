# Release policy

Empirical Finance Lab uses exact-commit release gates because research-software credibility depends on the scientific implementation, runtime, deployment artifact, documentation, and immutable release tag referring to the same governed state.

## Release states

### Development / unreleased (`0.0.0`)

Unreleased development work uses version `0.0.0`. Validated development deployments may exist, but they are not formal scholarly software releases.

### Stage VII — accepted release hardening

Stage VII hardened the accepted Stage III–VI scientific/application baseline and established tested-artifact deployment, privacy, provenance, reproducibility, onboarding, accessibility, and supply-chain controls.

The accepted Stage VII baseline is recorded in `docs/release_status.md`. Stage VII remains historical release-engineering authority; later stages may extend release-state metadata without redefining its scientific results.

### Stage VIII — accepted real-data external validation

Stage VIII independently validated EFL on five heterogeneous real CRSP event-study cases under a frozen design. Public evidence records locked specifications, hashes, numerical summaries, and parity results while licensed observation-level CRSP data remain private.

Stage VIII supports a tested-case numerical-parity claim. It does not imply CRSP/WRDS/vendor endorsement, representativeness of the five events, universal empirical validity, or causal identification.

### Stage IX — immutable historical `v0.1.0` release

`v0.1.0` is the first formal EFL release and is permanently fixed at commit `faf3dc6c5702dad3f5abd1dd15f7697fab5a5831`.

Later repository states must not move, recreate, or redefine the `v0.1.0` tag. The current Stage IX gate verifies the historical tag and its release metadata rather than requiring the current development line to remain version `0.1.0`.

### Stage X — governed `v0.1.1` patch release

v0.1.1 is an interoperability/usability/citation/discoverability patch. It does not change market-model estimation, abnormal returns, CAR, classical inference, PCG64 permutation inference, placebo computation, robustness computation, or the accepted Stage VIII numerical evidence.

The patch release requires:

- version `0.1.1` to be internally consistent across Python package/runtime metadata, browser expectations, project metadata, and citation metadata;
- the authoritative Stage III corpus to remain intact;
- all Stage IV econometric modules to remain byte-identical to the accepted frozen scientific tree;
- the exact v0.1.1 `__init__.py` release-metadata state to be enumerated by the closed Stage VI/Stage X gates;
- Stage V browser parity, Stage VI application gates, Stage VII release-hardening gates, and Stage VIII real-data evidence to remain green;
- the historical Stage IX v0.1.0 integrity gate to remain green;
- the Stage X patch-release gate to pass on the exact candidate commit;
- governed integration to `main`;
- fresh Stage III–X validation on the resulting exact `main` commit;
- immutable tag `v0.1.1` to point to that exact validated main commit;
- a tag-triggered Stage X gate to verify `tag == software version` and `tag target == exact current origin/main commit`; and
- the GitHub Release to be published from that already-validated tag.

The v0.1.1 tag must never be moved to a different commit.

## Release version authority

`pyproject.toml` and `src/empirical_finance_lab/__init__.py` must agree on the software version. `CITATION.cff` must cite the same release line. The private frontend workspace package version `0.0.0` is not the scholarly software-version authority; browser runtime and reproducibility outputs report the validated Python-core software version.

## Scientific-change rule

Golden/reference results are independent authority. They must not be regenerated merely because production code disagrees with them.

For v0.1.1, every Stage IV econometric module remains unchanged. The only allowed frozen-core delta is the exact `src/empirical_finance_lab/__init__.py` release-metadata state enumerated by the Stage VI/Stage X gates. Any future numerical or methodology change requires the classifications and evidence described in `CONTRIBUTING.md`.

The general browser estimation-window default may remain researcher-editable at `[-250,-30]`. The Stage VIII validation design `[-256,-46]` is evidence-specific and is not silently imposed as a universal research default.

## Dependency and supply-chain rule

Dependency changes follow `docs/governance/DEPENDENCY_UPDATE_POLICY.md`. Scientific Python/runtime changes are deliberate scientific-maintenance events, not ordinary automated dependency refreshes. External GitHub Actions remain pinned to approved full-length commit SHAs.

## Real-data licensing rule

Licensed CRSP observations and private Stage VIII derived input CSVs must not be committed, attached to public issues, or included in public release artifacts. Public validation claims must describe tested-case parity without implying vendor endorsement.

## Citation and archival rule

A formal GitHub release may exist without a DOI. `CITATION.cff` must identify the released version and release date.

If a version-specific archival DOI is later minted for v0.1.1, it must identify the exact immutable `v0.1.1` release. The DOI may be added to current metadata only after it actually exists. No placeholder, guessed, reserved-by-assumption, or unissued DOI may be advertised.

## External feedback rule

Researcher feedback remains open after release. Public issue forms must explicitly prohibit proprietary, licensed, confidential, and observation-level research data and should request minimal synthetic reproductions where possible.
