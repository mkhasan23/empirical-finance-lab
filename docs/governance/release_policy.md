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

A separate Public Beta waiting period is **not required** before the first formal release once Stage VIII and the complete release gates have passed. External issue discovery remains open after release.

### Stage IX — formal `v0.1.0` release

The first formal release requires:

- version `0.1.0` to be internally consistent across Python package/runtime metadata and citation metadata;
- the authoritative Stage III corpus to remain intact;
- all Stage IV econometric modules to remain byte-identical to the accepted frozen scientific tree;
- any release-time scientific-package metadata exception to be closed and exact, not an open path exemption;
- Stage V browser parity, Stage VI application gates, Stage VII release-hardening gates, and Stage VIII real-data evidence to remain green;
- the Stage IX release gate to pass on the exact candidate commit;
- governed integration to `main`;
- fresh Stage III–IX validation on the resulting exact `main` commit;
- immutable tag `v0.1.0` to point to that exact validated main commit;
- a tag-triggered Stage IX gate to verify `tag == software version` and `tag target == exact current origin/main commit`; and
- the GitHub Release to be published from that already-validated tag.

The formal release tag must never be moved to a different commit.

## Release version authority

`pyproject.toml` and `src/empirical_finance_lab/__init__.py` must agree on the software version. `CITATION.cff` must cite the same release line. The private frontend workspace package version is not the scholarly software-version authority; browser runtime and reproducibility outputs report the validated Python-core software version.

## Scientific-change rule

Golden/reference results are independent authority. They must not be regenerated merely because production code disagrees with them.

For `v0.1.0`, the Stage IV econometric implementation is unchanged. The only allowed frozen-core file delta is the exact `src/empirical_finance_lab/__init__.py` release-metadata state enumerated by the Stage VI/IX gates. Any future numerical or methodology change requires the classifications and evidence described in `CONTRIBUTING.md`.

## Dependency and supply-chain rule

Dependency changes follow `docs/governance/DEPENDENCY_UPDATE_POLICY.md`. Scientific Python/runtime changes are deliberate scientific-maintenance events, not ordinary automated dependency refreshes. External GitHub Actions remain pinned to approved full-length commit SHAs.

## Real-data licensing rule

Licensed CRSP observations and private Stage VIII derived input CSVs must not be committed, attached to public issues, or included in public release artifacts. Public validation claims must describe tested-case parity without implying vendor endorsement.

## Citation and archival rule

The formal GitHub release may exist without a DOI. `CITATION.cff` must identify the released version and release date.

If a version-specific archival DOI is later minted, it must identify the exact immutable `v0.1.0` release. The DOI may be added to current metadata only after it actually exists. No placeholder, guessed, or unissued DOI may be advertised.

## External feedback rule

Researcher feedback remains open after release. Public issue forms must explicitly prohibit proprietary, licensed, confidential, and observation-level research data and should request minimal synthetic reproductions where possible.
