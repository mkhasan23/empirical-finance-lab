#!/usr/bin/env python3
"""Write machine-readable Stage VII F2 evidence for the exact CI commit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "efl-stage7-acceptance-evidence-1"
DIST_SCHEMA = "efl-stage7-dist-manifest-1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_PAGE_PREFIX = "https://mkhasan23.github.io/empirical-finance-lab/"
ACCEPTED_STAGE7_BASELINE = "08d8b1b8f5953b1e5cf93ec6a298a731757e0c87"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"missing required environment variable {name}")
    return value


def command_version(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def workflow_action_pins() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    pattern = re.compile(r"^\s*-?\s*uses:\s*([^\s@]+)@([^\s#]+)")
    for workflow in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        for line in workflow.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if not match:
                continue
            action, ref = match.groups()
            if action.startswith("./"):
                continue
            if not SHA40.fullmatch(ref):
                raise ValueError(
                    f"external action is not pinned to a full SHA: {workflow.name}: {action}@{ref}"
                )
            records.append(
                {"workflow": workflow.name, "action": action, "sha": ref}
            )
    if not records:
        raise ValueError("no external action pins found")
    return records


def locked_frontend_versions() -> dict[str, str]:
    lock_path = ROOT / "web" / "package-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    root = lock.get("packages", {}).get("", {})
    deps = root.get("devDependencies", {})
    expected = {
        "@playwright/test": "1.62.0",
        "@types/node": "24.13.3",
        "typescript": "5.9.3",
        "vite": "8.2.1",
        "vitest": "4.1.10",
    }
    if deps != expected:
        raise ValueError(f"frontend lock root devDependencies drifted: {deps!r}")
    return dict(sorted(deps.items()))


def locked_browser_versions() -> dict[str, dict[str, str]]:
    browser_path = ROOT / "web" / "node_modules" / "playwright-core" / "browsers.json"
    if not browser_path.is_file():
        raise ValueError("playwright-core/browsers.json missing; run npm ci before evidence writer")
    raw = json.loads(browser_path.read_text(encoding="utf-8"))
    browsers = raw.get("browsers", [])
    wanted = {"chromium", "firefox", "webkit"}
    result: dict[str, dict[str, str]] = {}
    for item in browsers:
        name = str(item.get("name", ""))
        if name not in wanted:
            continue
        result[name] = {
            "browser_version": str(item.get("browserVersion", "")),
            "playwright_revision": str(item.get("revision", "")),
        }
    if set(result) != wanted:
        raise ValueError(f"missing locked browser metadata: found {sorted(result)}")
    for name, metadata in result.items():
        if not metadata["browser_version"] or not metadata["playwright_revision"]:
            raise ValueError(f"incomplete browser metadata for {name}: {metadata!r}")
    return dict(sorted(result.items()))


def scientific_pins() -> dict[str, str]:
    workflow = (ROOT / ".github" / "workflows" / "release-hardening.yml").read_text(
        encoding="utf-8"
    )
    tokens = {
        "python": "3.13",
        "numpy": "2.3.5",
        "scipy": "1.17.0",
        "pytest": "9.0.2",
        "coverage": "7.13.3",
    }
    required = (
        "python-version: '3.13'",
        "numpy==2.3.5",
        "scipy==1.17.0",
        "pytest==9.0.2",
        "coverage==7.13.3",
    )
    missing = [token for token in required if token not in workflow]
    if missing:
        raise ValueError(f"scientific pin tokens missing from release-hardening workflow: {missing}")
    return tokens


def load_dist_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != DIST_SCHEMA:
        raise ValueError("unexpected Stage VII dist manifest schema")
    if manifest.get("artifact_root") != "dist":
        raise ValueError("unexpected Stage VII dist artifact_root")
    if not isinstance(manifest.get("file_count"), int) or manifest["file_count"] <= 0:
        raise ValueError("invalid Stage VII dist file_count")
    if not isinstance(manifest.get("total_bytes"), int) or manifest["total_bytes"] <= 0:
        raise ValueError("invalid Stage VII dist total_bytes")
    tree_sha = str(manifest.get("tree_sha256", ""))
    if not SHA64.fullmatch(tree_sha):
        raise ValueError("invalid Stage VII dist tree SHA-256")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != manifest["file_count"]:
        raise ValueError("Stage VII dist file list/count mismatch")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    try:
        commit = required_env("EFL_BUILD_COMMIT")
        if not SHA40.fullmatch(commit):
            raise ValueError("EFL_BUILD_COMMIT is not a lowercase 40-character SHA")

        repository = required_env("GITHUB_REPOSITORY")
        run_id = int(required_env("GITHUB_RUN_ID"))
        run_attempt = int(required_env("GITHUB_RUN_ATTEMPT"))
        workflow = required_env("GITHUB_WORKFLOW")
        ref = required_env("GITHUB_REF")
        page_url = required_env("EFL_STAGE7_PAGE_URL")
        if not page_url.startswith(EXPECTED_PAGE_PREFIX):
            raise ValueError(f"unexpected GitHub Pages URL: {page_url}")
        is_main = ref == "refs/heads/main"

        job_results = {
            "build": required_env("EFL_STAGE7_BUILD_RESULT"),
            "deploy": required_env("EFL_STAGE7_DEPLOY_RESULT"),
            "verify_live": required_env("EFL_STAGE7_VERIFY_LIVE_RESULT"),
        }
        if set(job_results.values()) != {"success"}:
            raise ValueError(f"Stage VII dependency jobs are not all successful: {job_results}")

        manifest = load_dist_manifest(args.manifest)
        frontend = locked_frontend_versions()
        browsers = locked_browser_versions()
        actions = workflow_action_pins()
        scientific = scientific_pins()

        tracked_hashes = {}
        for relative in (
            ".github/workflows/release-hardening.yml",
            "CITATION.cff",
            "REPOSITORY_MANIFEST.txt",
            "pyproject.toml",
            "validation/manifest.json",
            "web/package-lock.json",
        ):
            path = ROOT / relative
            if not path.is_file():
                raise ValueError(f"required evidence-hash path missing: {relative}")
            tracked_hashes[relative] = sha256(path)

        payload: dict[str, Any] = {
            "schema_version": SCHEMA,
            "candidate": {
                "repository": repository,
                "commit": commit,
                "ref": ref,
                "workflow": workflow,
                "run_id": run_id,
                "run_attempt": run_attempt,
                "page_url": page_url,
            },
            "stage7_dependency_jobs": job_results,
            "production_artifact": {
                "manifest_schema": manifest["schema_version"],
                "file_count": manifest["file_count"],
                "total_bytes": manifest["total_bytes"],
                "tree_sha256": manifest["tree_sha256"],
            },
            "toolchain": {
                "evidence_python": platform.python_version(),
                "node": command_version(["node", "--version"]),
                "npm": command_version(["npm", "--version"]),
                "scientific_pins": scientific,
                "frontend_dev_pins": frontend,
                "playwright_browsers": browsers,
            },
            "repository_hashes": dict(sorted(tracked_hashes.items())),
            "external_action_pins": actions,
            "acceptance_boundary": {
                "accepted_stage7_baseline": ACCEPTED_STAGE7_BASELINE,
                "branch_candidate_evidence_complete": True,
                "stage7_accepted": is_main,
                "public_beta": False,
                "formal_v0_1_0": False,
                "version_specific_doi": False,
                "main_integration_and_main_rerun_required": not is_main,
                "repository_governance_settings_machine_verified": False,
            },
            "limitations": [
                (
                    "This artifact proves the exact deployed main commit under the Stage VII CI contract; "
                    "repository-level Pages cleanup and full-SHA enforcement are administrator-confirmed "
                    "in the committed acceptance record and are not machine-read by this workflow."
                    if is_main
                    else
                    "This artifact proves the exact deployed branch commit under the Stage VII CI contract; "
                    "Stage VII remains accepted at the separately recorded main baseline."
                ),
                "Automated accessibility checks are not a WCAG certification or manual assistive-technology study.",
                "Pinned runtime initialization may use the allowed jsDelivr Pyodide host; scientific analysis-phase network traffic must remain zero.",
                "Prior WebKit cold-start/timeout events were resolved by successful same-code reruns and remain disclosed in the committed evidence record.",
            ],
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("STAGE VII-F2 CI EVIDENCE: WRITE PASS")
        print(f" - commit: {commit}")
        print(f" - ref: {ref}")
        print(f" - stage7 accepted: {is_main}")
        print(f" - accepted baseline: {ACCEPTED_STAGE7_BASELINE}")
        print(f" - run: {run_id} attempt {run_attempt}")
        print(f" - production tree: {manifest['tree_sha256']}")
        print(f" - browsers: {', '.join(f'{k} {v["browser_version"]}' for k, v in browsers.items())}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"STAGE VII-F2 CI EVIDENCE: FAIL - {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
