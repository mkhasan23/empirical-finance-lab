# Dependency and GitHub Actions Update Policy

Status: Stage VII-C2 release-hardening policy. This policy governs update proposals before Public Beta and formal `v0.1.0`.

## Principles

Empirical Finance Lab separates **scientific dependencies** from **tooling and delivery dependencies**. Dependency freshness is not allowed to override numerical reproducibility, browser parity, or the frozen validation corpus.

Dependabot pull requests are proposals, not merge authorization. Every accepted dependency or GitHub Actions update must preserve the relevant static gates and pass Stages III through VII before integration.

## Scientific Python

Scientific Python is not on automatic version updates.

`pyproject.toml` expresses the supported package ranges, while CI uses the exact validated reference environment for numerical gates. NumPy, SciPy, pytest, coverage, Python-runtime, Pyodide, or other scientific-runtime changes require an intentional research-software maintenance change with parity, known-answer, browser, and reproducibility evidence. A security alert affecting scientific Python must be triaged promptly, but remediation still requires scientific revalidation rather than an unreviewed version bump.

## Frontend development tooling

The browser application has no runtime npm dependencies. Development/test tooling is exact-pinned in `web/package.json` and `web/package-lock.json`, installed with `npm ci`, and monitored weekly by Dependabot from `/web`.

A proposed npm update must:
- preserve the lockfile/package agreement;
- preserve zero runtime npm dependencies;
- pass TypeScript and unit tests;
- pass Stage V parity/privacy in Chromium, Firefox, and WebKit;
- pass Stage VI application journeys in Chromium, Firefox, and WebKit; and
- pass Stage VII production, deployment, live-byte, CSP, KA-003, and privacy gates when the change affects the deployed artifact or browser toolchain.

## GitHub Actions

Every external action used by `.github/workflows` is pinned to a **full-length commit SHA** and carries a human-readable major-version annotation. The Stage VII-C2 gate maintains the approved SHA allowlist.

Dependabot checks the `github-actions` ecosystem weekly. A proposed action update is not accepted merely because Dependabot opened it. The new SHA must be reviewed as an upstream release from the expected action repository, the C2 allowlist must be deliberately updated, and Stages III through VII must pass.

After C2 is integrated into the default branch, repository Actions settings should enable **Require actions to be pinned to a full-length commit SHA**. Do not enable that repository-wide enforcement while the default branch still contains mutable action tags.

## Vulnerability monitoring

Repository security settings should enable the dependency graph, Dependabot alerts, and Dependabot security updates where available. Alerts do not change scientific or tooling versions by themselves; they create a triage obligation.

For a vulnerability:
1. identify the affected dependency and whether it is scientific authority, development tooling, or delivery infrastructure;
2. determine whether the vulnerable component is reachable in EFL's deployed/runtime threat model;
3. identify an upstream fixed version or commit;
4. apply the smallest compatible remediation on a branch;
5. run the full required validation chain; and
6. record any residual limitation or upstream warning.

The current upstream `Buffer()` warning from `actions/download-artifact` and the `punycode` warning from `actions/deploy-pages` are tracked as upstream maintenance signals; they are not by themselves evidence of EFL numerical or privacy failure.
