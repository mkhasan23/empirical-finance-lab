# Stage VII — Release Hardening and Deployment Foundation

Status: implementation candidate on `stage-vii-release-hardening`. This stage does **not** declare Empirical Finance Lab a public beta or a formal `v0.1.0` release.

## Purpose

Stage VII hardens the accepted Stage III–VI scientific/application stack for reproducible static deployment. The scientific authority remains the frozen Python core. Stage VII does not add econometric methods, alter validated fixtures, change RNG behavior, or redefine AnalysisID/ExecutionID.

## Deployment target

The repository-site target is the GitHub Pages project path:

`https://mkhasan23.github.io/empirical-finance-lab/`

The Vite production mode must therefore use `/empirical-finance-lab/` as its base path. Ordinary Stage V/VI builds remain rooted at `/` so inherited browser gates retain their accepted behavior.

## Candidate-build contract

A Stage VII candidate must:

- preserve the exact ordinary `vite build` script used by the accepted Stage V/VI gates;
- build the Pages candidate separately with `vite build --mode github-pages`;
- preview that candidate with the same `github-pages` mode so the local server enforces the repository subpath;
- install frontend dependencies with `npm ci` from the committed lockfile;
- pass the accepted Stage VI static gate before Stage VII checks;
- run TypeScript and unit tests;
- build the production candidate once;
- record a deterministic SHA-256 manifest of every production file;
- run a Chromium production-like smoke test at `/empirical-finance-lab/`;
- prove KA-003 parity under the pinned Pyodide/Python/NumPy/SciPy runtime;
- prove zero network requests during the scientific analysis phase;
- verify the production tree is unchanged after the smoke test;
- upload the tested dist and its manifest as separate CI artifacts.

## Browser security boundary contract

The Stage VII Pages candidate must emit an enforcing document **Content Security Policy** and **Referrer Policy** through Vite's HTML transformation before resource-loading tags.

The document CSP must retain the following policy surface:

`default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self'; frame-src 'none'; media-src 'none'; manifest-src 'self'; form-action 'self'`

The policy must not contain `unsafe-inline` or `unsafe-eval`, and it must not grant the document direct access to `cdn.jsdelivr.net`. The Referrer Policy must be `no-referrer`.

The `worker-src 'self'` rule protects creation of the same-origin EFL scientific worker. The worker's internal network policy is a separate execution-context boundary: EFL does not claim that the document CSP constrains normal dedicated-worker fetches. Worker initialization remains governed by version-controlled worker code, the same-origin `efl-core.json` authority check, the pinned `cdn.jsdelivr.net` Pyodide endpoint, source/bundle hash verification, and browser network auditing.

Both the local production-subpath test and the real deployed-site test must assert the exact document CSP and Referrer Policy, listen for `securitypolicyviolation`, and fail on any document CSP violation while preserving the existing pinned-runtime, KA-003, and zero-analysis-network requirements.

The Stage VII-C1 static security gate must run automatically before `build:pages` so a Pages artifact cannot be produced from a candidate whose documented policy, Vite injection, or production/live assertions have drifted.

## Supply-chain governance contract

Every external action invoked from `.github/workflows` must use a **full-length commit SHA**. Stage VII-C2 freezes the action commits that were already exercised successfully by the accepted C1 run and rejects mutable tags, malformed `uses:` references, unapproved external actions, and unexpected SHA/version-annotation drift.

Dependabot version updates are intentionally scoped to:
- npm development/test tooling under `/web`, checked weekly; and
- GitHub Actions under `/`, checked weekly.

Scientific Python is not placed on automatic version updates. Changes to the numerical environment, Pyodide runtime, Python, NumPy, SciPy, or related scientific authority require deliberate maintenance and scientific parity evidence.

Dependabot proposals do not bypass governance. An accepted dependency or action update must preserve its applicable static contracts and pass Stages III through VII before integration. The detailed review and vulnerability-triage policy is maintained in `docs/governance/DEPENDENCY_UPDATE_POLICY.md`.

After C2 is merged to the default branch, repository administrators should enable the GitHub Actions setting requiring full-length SHA pins. Dependency graph, Dependabot alerts, and Dependabot security updates should be enabled in repository security settings; those settings create monitoring/triage obligations but do not override EFL's validation requirements.

## Build provenance authority contract

Stage VII-D1 gives the browser production artifact a deterministic, verifiable identity tied to the **exact checked-out Git commit**. The release-hardening workflow exports `EFL_BUILD_COMMIT=${{ github.sha }}` and verifies that it equals `git rev-parse HEAD` before the candidate build begins. A GitHub Pages build must refuse to proceed unless that value is a lowercase 40-character Git commit SHA.

Vite embeds three provenance fields into the application bundle: build commit, build mode, and build source. Build mode is the Vite mode and the production candidate must report `github-pages`; build source is `github-actions` for the validated Pages artifact. The production identity deliberately contains **no timestamps** and **no workflow-run identifiers**, so rebuilding the same commit under the same controlled toolchain does not acquire irrelevant time-dependent provenance.

The dedicated scientific worker must set the embedded build commit into Python as `EFL_BUILD_COMMIT` before the authoritative `empirical_finance_lab` analysis path executes. The worker must verify that Python reads back exactly the same commit and expose commit/mode/source in the browser runtime manifest. The frozen Python reproducibility code remains unchanged: its existing runtime manifest consumes `EFL_BUILD_COMMIT`, and its existing ExecutionID definition already incorporates `build_commit`.

D1 does not redefine **AnalysisID** or **ExecutionID**. AnalysisID remains a function of canonical data plus locked specification. ExecutionID continues to use the existing Stage IV definition and now receives the build-commit input that definition was designed to include for production browser runs. Scientific parity comparisons continue to exclude environment and ExecutionID fields while retaining all scientific quantities and AnalysisID.

The reproducibility exporter must require the browser runtime commit and scientific-core environment commit to agree. Its manifest, environment file, README, and citation text must record the same build provenance. A Pages-mode export with an unset or malformed commit must fail safely rather than emit ambiguous provenance.

Both the local production-subpath gate and the real deployed-site gate must assert that:
- runtime build commit equals `EFL_BUILD_COMMIT` for the workflow run;
- build mode is `github-pages`;
- build source is `github-actions`;
- the scientific-core reproducibility environment reports that same build commit;
- AnalysisID and ExecutionID remain well-formed; and
- existing KA-003 parity, CSP, and zero-analysis-network requirements remain green.

## Deployment contract

The deploy job must consume the exact build-job artifact. It must not rebuild the application. Before packaging for GitHub Pages, it re-verifies the downloaded dist against the build-job manifest.

During Stage VII candidate validation, deployment is allowed only when either:

1. a `workflow_dispatch` run explicitly sets `deploy=true` after the workflow is available from the default branch;
2. a push to `stage-vii-release-hardening` carries the deliberate commit-message marker `[deploy-candidate]`; or
3. the workflow runs from a push to `main` after Stage VII has been accepted and merged.

Ordinary feature-branch pushes without `[deploy-candidate]` build and test but do not deploy. The `github-pages` environment must permit the Stage VII branch while candidate deployments are being validated; that temporary branch rule can be removed after Stage VII is integrated.

The Pages deployment job uses the `github-pages` environment and only the permissions required for Pages deployment.

## Live deployed-site verification contract

A successful Pages deployment is not sufficient by itself. The post-deployment gate must run against the actual HTTPS Pages URL returned by `actions/deploy-pages` and must not start a local preview server or rebuild the app.

The live gate must:

- download the build job's authoritative Stage VII dist manifest;
- verify the manifest's schema, file count, total bytes, and tree SHA-256 integrity;
- fetch every published production file from the real Pages URL with cache-busting and compare its byte size and SHA-256 with the tested build manifest;
- tolerate a short Pages/CDN propagation interval but fail if the live artifact does not converge to the tested manifest;
- open the actual deployed site in Chromium over HTTPS;
- confirm the `/empirical-finance-lab/` base path and document base URI;
- verify the exact Stage VII document CSP and `no-referrer` policy and require no document `securitypolicyviolation` events;
- initialize the pinned Pyodide/Python/NumPy/SciPy runtime;
- permit initialization network traffic only to the Pages project path and the pinned jsDelivr runtime host;
- confirm that the authoritative `efl-core.json` is fetched from the live repository subpath;
- run KA-003 and require zero parity mismatches; and
- require zero network requests during the scientific analysis phase.

This post-deployment evidence closes the gap between a locally previewed production artifact and the bytes and behavior actually served to users.

## Manual repository prerequisite

GitHub Pages must be enabled once in repository settings:

**Settings → Pages → Build and deployment → Source → GitHub Actions**

For pre-merge Stage VII candidate deployment, the `github-pages` environment must also allow `stage-vii-release-hardening` under **Settings → Environments → github-pages → Deployment branches and tags**.

Do not perform a Stage VII candidate deployment until the branch build gate is green.

## Current release status

During Stage VII the app remains a pre-release/public-beta candidate and remains `noindex,nofollow`. DOI creation and the formal `v0.1.0` release remain later milestones.
