from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_STAGE7_BASELINE = "08d8b1b8f5953b1e5cf93ec6a298a731757e0c87"
STAGE7_BASELINE_TRACKED_PATH_COUNT = 206


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        raise SystemExit(f"STAGE VII-F2 EVIDENCE GATE: FAIL\n - missing {path}")
    return target.read_text(encoding="utf-8")


def require(text: str, token: str, label: str, errors: list[str]) -> None:
    if token not in text:
        errors.append(f"{label}: missing {token!r}")


def reject(text: str, token: str, label: str, errors: list[str]) -> None:
    if token in text:
        errors.append(f"{label}: forbidden token {token!r}")


def git_tracked_files() -> list[str] | None:
    if not (ROOT / ".git").exists():
        return None
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, stderr=subprocess.STDOUT
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            "STAGE VII-F2 EVIDENCE GATE: FAIL\n"
            f" - unable to read tracked-file inventory: {exc}"
        ) from exc
    return sorted(item for item in raw.decode("utf-8").split("\0") if item)


def main() -> None:
    errors: list[str] = []

    report = read("docs/STAGE_VII_EVIDENCE_REPORT.md")
    for token in (
        "27ac2c64b3accc0af6bd26f7986fd5bf4ac21af5",
        "32067482245",
        "32067482240",
        "32067482242",
        "32067482243",
        "32067482252",
        "9d69f206c107dc7cb1c89984cfdf973561aaf2360e1963f154f1aa3820748e0a",
        "9300488558",
        "sha256:c4556aab6138838ffba6d01c44e7bc7329ffaeeb68d601926bedb238c6da2995",
        "9300488938",
        "sha256:bb1c8a9da2ad2faa274d126c5b71066d8d9de638990c166c9bf2802daa0e23d6",
        "9300495320",
        "sha256:ec59002a5cba9aa76b3715393679cae0384a5a32f62d4216835b696cc20a7baf",
        "https://mkhasan23.github.io/empirical-finance-lab/",
        "browser `151.0.7922.34`, revision `1234`",
        "browser `153.0`, revision `1538`",
        "browser `26.5`, revision `2336`",
        "cold-start/runtime transient",
        "No application, scientific-core, runtime-pin, watchdog, or F1 code change was made",
        "not a WCAG certification",
        "stage7-acceptance-evidence",
        "Stage VII branch candidate ready for governed integration",
    ):
        require(report, token, "evidence report", errors)
    reject(report, "Stage VII is accepted", "evidence report", errors)

    checklist = read("docs/STAGE_VII_ACCEPTANCE_CHECKLIST.md")
    for token in (
        "- [x] Stage III corpus integrity preserved.",
        "- [x] Scientific analysis-phase network traffic is zero.",
        f"- [x] Exact F2 commit `7236cb37a971edceed99981dd7d17e631868ee2b` passed Stages III–VII.",
        f"- [x] Exact F2 Stage VII run `32073099350` passed build, deployment, and live verification on attempt 2.",
        f"artifact `9303611739` with digest `sha256:18df6b9b058de4d16d91d6c070996bb3356ba8f578440bb7f4b5365ea4978b5d`",
        "- [x] Governed integration of the fully green Stage VII feature branch to `main`.",
        f"- [x] Stages III–VII reran successfully on accepted baseline `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`",
        "repository administrator-confirmed",
        f"**Stage VII is accepted at baseline `08d8b1b8f5953b1e5cf93ec6a298a731757e0c87`.**",
    ):
        require(checklist, token, "acceptance checklist", errors)

    spec = read("docs/specifications/STAGE_VII_F2_EVIDENCE_ACCEPTANCE.md")
    for token in (
        "Self-reference rule",
        "efl-stage7-acceptance-evidence-1",
        "Stage VII branch candidate ready for governed integration.",
        "Stage VII acceptance requires integration to `main`",
        "`src/empirical_finance_lab/**`",
        "`web/package.json` or `web/package-lock.json`",
    ):
        require(spec, token, "F2 specification", errors)

    writer = read("tools/write_stage7_f2_ci_evidence.py")
    for token in (
        'SCHEMA = "efl-stage7-acceptance-evidence-1"',
        'DIST_SCHEMA = "efl-stage7-dist-manifest-1"',
        f'ACCEPTED_STAGE7_BASELINE = "08d8b1b8f5953b1e5cf93ec6a298a731757e0c87"',
        'required_env("EFL_BUILD_COMMIT")',
        'required_env("GITHUB_RUN_ID")',
        'required_env("EFL_STAGE7_PAGE_URL")',
        'is_main = ref == "refs/heads/main"',
        '"stage7_dependency_jobs"',
        '"playwright_browsers"',
        '"external_action_pins"',
        '"stage7_accepted": is_main',
        '"main_integration_and_main_rerun_required": not is_main',
        '"repository_governance_settings_machine_verified": False',
        '"release_candidate_v0_1_0"',
        '"stage9_release_tag_required"',
    ):
        require(writer, token, "F2 evidence writer", errors)

    workflow = read(".github/workflows/release-hardening.yml")
    if workflow.count("python tools/check_stage7_f2_evidence_gate.py") != 1:
        errors.append("release-hardening workflow: expected exactly one F2 static-gate invocation")
    for token in (
        "  evidence:\n    needs: [build, deploy, verify-live]",
        "EFL_STAGE7_BUILD_RESULT: ${{ needs.build.result }}",
        "EFL_STAGE7_DEPLOY_RESULT: ${{ needs.deploy.result }}",
        "EFL_STAGE7_VERIFY_LIVE_RESULT: ${{ needs.verify-live.result }}",
        "EFL_STAGE7_PAGE_URL: ${{ needs.deploy.outputs.page_url }}",
        "python tools/write_stage7_f2_ci_evidence.py",
        "name: stage7-acceptance-evidence",
        "retention-days: 30",
    ):
        require(workflow, token, "release-hardening workflow", errors)

    action_pattern = re.compile(r"^\s*-?\s*uses:\s*([^\s@]+)@([^\s#]+)", re.MULTILINE)
    for action, ref in action_pattern.findall(workflow):
        if action.startswith("./"):
            continue
        if not re.fullmatch(r"[0-9a-f]{40}", ref):
            errors.append(f"release-hardening workflow: mutable/malformed action ref {action}@{ref}")

    status = read("docs/release_status.md")
    for token in (
        "Accepted Stage VII release-hardening baseline",
        ACCEPTED_STAGE7_BASELINE,
        "STAGE_VII_EVIDENCE_REPORT.md",
        "STAGE_VII_ACCEPTANCE_CHECKLIST.md",
        "Repository administrator-confirmed",
        "v0.1.0",
        "Stage VIII",
        "Stage IX",
        "Formal release tag: `v0.1.0`",
        "No version-specific DOI is claimed unless",
    ):
        require(status, token, "docs/release_status.md", errors)
    reject(status, "Stage VII as a whole is **not yet accepted**", "docs/release_status.md", errors)

    citation = read("CITATION.cff")
    require(citation, "version: 0.1.0", "CITATION.cff", errors)
    require(citation, "date-released: 2026-08-19", "CITATION.cff", errors)
    require(citation, "/releases/tag/v0.1.0", "CITATION.cff", errors)

    manifest_lines = [
        line.strip()
        for line in read("REPOSITORY_MANIFEST.txt").splitlines()
        if line.strip()
    ]
    if manifest_lines != sorted(manifest_lines):
        errors.append("REPOSITORY_MANIFEST.txt: entries are not lexicographically sorted")
    if len(manifest_lines) != len(set(manifest_lines)):
        errors.append("REPOSITORY_MANIFEST.txt: duplicate entries found")
    if len(manifest_lines) < STAGE7_BASELINE_TRACKED_PATH_COUNT:
        errors.append(
            "REPOSITORY_MANIFEST.txt: tracked-path inventory shrank below the accepted "
            f"Stage VII baseline ({STAGE7_BASELINE_TRACKED_PATH_COUNT}); "
            f"found {len(manifest_lines)}"
        )
    required_manifest_entries = {
        "docs/STAGE_VII_ACCEPTANCE_CHECKLIST.md",
        "docs/STAGE_VII_EVIDENCE_REPORT.md",
        "docs/specifications/STAGE_VII_F2_EVIDENCE_ACCEPTANCE.md",
        "tools/check_stage7_f2_evidence_gate.py",
        "tools/write_stage7_f2_ci_evidence.py",
    }
    missing = sorted(required_manifest_entries.difference(manifest_lines))
    if missing:
        errors.append("REPOSITORY_MANIFEST.txt: missing F2 entries: " + ", ".join(missing))

    tracked = git_tracked_files()
    if tracked is not None and manifest_lines != tracked:
        manifest_set = set(manifest_lines)
        tracked_set = set(tracked)
        missing_from_manifest = sorted(tracked_set - manifest_set)
        extra_in_manifest = sorted(manifest_set - tracked_set)
        errors.append(
            "REPOSITORY_MANIFEST.txt: does not equal git ls-files"
            + (f"; missing={missing_from_manifest}" if missing_from_manifest else "")
            + (f"; extra={extra_in_manifest}" if extra_in_manifest else "")
        )

    if errors:
        print("STAGE VII-F2 EVIDENCE GATE: FAIL")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("STAGE VII-F2 EVIDENCE GATE: PASS")
    print(" - validated predecessor ledger: PASS")
    print(" - WebKit rerun disclosure: PASS")
    print(" - exact-commit CI evidence contract: PASS")
    print(" - accepted Stage VII release-state boundary: PASS")
    print(f" - repository manifest: {len(manifest_lines)} tracked paths")
    print(" - main-integration acceptance record: PASS")


if __name__ == "__main__":
    main()
