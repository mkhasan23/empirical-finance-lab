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

## Deployment contract

The deploy job must consume the exact build-job artifact. It must not rebuild the application. Before packaging for GitHub Pages, it re-verifies the downloaded dist against the build-job manifest.

Feature-branch pushes build and test but do not deploy. Deployment is allowed only when either:

1. a `workflow_dispatch` run explicitly sets `deploy=true`, or
2. the workflow runs from a push to `main` after Stage VII has been accepted and merged.

The Pages deployment job uses the `github-pages` environment and only the permissions required for Pages deployment.

## Manual repository prerequisite

GitHub Pages must be enabled once in repository settings:

**Settings → Pages → Build and deployment → Source → GitHub Actions**

Do not perform the first Stage VII candidate deployment until the branch build gate is green.

## Current release status

During Stage VII the app remains a pre-release/public-beta candidate and remains `noindex,nofollow`. DOI creation and the formal `v0.1.0` release remain later milestones.
