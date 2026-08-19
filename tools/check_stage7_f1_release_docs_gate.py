from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_STAGE7_BASELINE = "08d8b1b8f5953b1e5cf93ec6a298a731757e0c87"
CURRENT_VERSION = "0.1.1"
CURRENT_TAG = "v0.1.1"
HISTORICAL_TAG = "v0.1.0"


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        raise SystemExit(f"STAGE VII-F1 RELEASE DOCUMENTATION GATE: FAIL\n - missing {path}")
    return target.read_text(encoding="utf-8")


def require(text: str, token: str, label: str, errors: list[str]) -> None:
    if token not in text:
        errors.append(f"{label}: missing {token!r}")


def reject(text: str, token: str, label: str, errors: list[str]) -> None:
    if token in text:
        errors.append(f"{label}: stale/forbidden token {token!r}")


def git_tracked_files() -> list[str] | None:
    if not (ROOT / ".git").exists():
        return None
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            stderr=subprocess.STDOUT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            "STAGE VII-F1 RELEASE DOCUMENTATION GATE: FAIL\n"
            f" - unable to read tracked-file inventory: {exc}"
        ) from exc
    return sorted(item for item in raw.decode("utf-8").split("\0") if item)


def main() -> None:
    errors: list[str] = []

    root_readme = read("README.md")
    for token in (
        "Stage VII release",
        ACCEPTED_STAGE7_BASELINE,
        "v0.1.1 validated patch release line",
        "v0.1.1 interoperability and usability patch",
        "five heterogeneous real CRSP event-study cases",
        "2.7755575615628914e-16",
        "Researcher feedback",
        "docs/quickstart.md",
        "docs/release_status.md",
        "SECURITY.md",
        "docs/governance/release_policy.md",
        "https://mkhasan23.github.io/empirical-finance-lab/",
        HISTORICAL_TAG,
    ):
        require(root_readme, token, "README.md", errors)
    reject(root_readme, "pre-release citation status", "README.md", errors)
    reject(root_readme, "exact pre-release boundary", "README.md", errors)

    web_readme = read("web/README.md")
    for token in (
        "# Empirical Finance Lab v0.1.1 browser application",
        ACCEPTED_STAGE7_BASELINE,
        CURRENT_TAG,
        HISTORICAL_TAG,
        "Five heterogeneous real CRSP event-study cases",
        "Researcher feedback",
        "../docs/quickstart.md",
        "../docs/release_status.md",
        "npm run build:pages",
        "npm run test:e2e:stage7",
        "python tools/check_stage9_release_gate.py",
        "python tools/check_stage10_patch_release_gate.py",
    ):
        require(web_readme, token, "web/README.md", errors)

    changelog = read("CHANGELOG.md")
    for token in (
        "## 0.1.1 - 2026-08-19",
        "deterministic browser date interoperability",
        "Stage X patch-release governance",
        "[-250,-30]",
        "## 0.1.0 - 2026-08-19",
        "five heterogeneous CRSP event studies",
        "No version-specific DOI",
    ):
        require(changelog, token, "CHANGELOG.md", errors)

    status = read("docs/release_status.md")
    for token in (
        "v0.1.1 validated patch release line",
        ACCEPTED_STAGE7_BASELINE,
        "a694d49df9716f9f87d359385598237363e4c3fc",
        "621b0cafdcad3711d2aba3bef698d2e78d022144",
        "faf3dc6c5702dad3f5abd1dd15f7697fab5a5831",
        "Stage VIII",
        "Stage X",
        "Intended patch release tag: `v0.1.1`",
        "No version-specific DOI is claimed unless",
        "https://mkhasan23.github.io/empirical-finance-lab/",
    ):
        require(status, token, "docs/release_status.md", errors)

    policy = read("docs/governance/release_policy.md")
    for token in (
        "Stage VII — accepted release hardening",
        "Stage VIII — accepted real-data external validation",
        "Stage IX — immutable historical `v0.1.0` release",
        "Stage X — governed `v0.1.1` patch release",
        "version `0.0.0`",
        "tag == software version",
        "exact-commit",
        "CRSP/WRDS/vendor endorsement",
    ):
        require(policy, token, "release policy", errors)

    citation = read("CITATION.cff")
    for token in (
        "version: 0.1.1",
        "date-released: 2026-08-19",
        "/releases/tag/v0.1.1",
        "Muhammad Kamrul",
    ):
        require(citation, token, "CITATION.cff", errors)

    spec = read("docs/specifications/STAGE_VII_F1_RELEASE_DOCUMENTATION.md")
    require(spec, "Passing F1 does **not** complete Stage VII", "F1 specification", errors)
    require(spec, "git ls-files", "F1 specification", errors)

    manifest_lines = [
        line.strip()
        for line in read("REPOSITORY_MANIFEST.txt").splitlines()
        if line.strip()
    ]
    if manifest_lines != sorted(manifest_lines):
        errors.append("REPOSITORY_MANIFEST.txt: entries are not lexicographically sorted")
    if len(manifest_lines) != len(set(manifest_lines)):
        errors.append("REPOSITORY_MANIFEST.txt: duplicate entries found")
    required_manifest_entries = {
        ".github/dependabot.yml",
        ".github/workflows/release-hardening.yml",
        ".github/workflows/formal-release.yml",
        ".github/workflows/patch-release.yml",
        ".github/ISSUE_TEMPLATE/researcher_feedback.yml",
        "docs/quickstart.md",
        "docs/release_status.md",
        "docs/specifications/STAGE_VII_F1_RELEASE_DOCUMENTATION.md",
        "docs/specifications/STAGE_IX_FORMAL_RELEASE.md",
        "docs/specifications/STAGE_X_V0.1.1_PATCH_RELEASE.md",
        "examples/efl_tutorial_synthetic.csv",
        "tools/check_stage7_f1_release_docs_gate.py",
        "tools/check_stage9_release_gate.py",
        "tools/check_stage10_patch_release_gate.py",
        "web/package-lock.json",
        "web/playwright.stage7.live.config.ts",
        "web/public/sitemap.xml",
        "web/src/buildProvenance.ts",
        "web/src/reproRoundTrip.ts",
        "web/src/storedZip.ts",
        "web/tests-live/stage7.live.spec.ts",
        "web/tests/stage7.spec.ts",
    }
    missing_manifest = sorted(required_manifest_entries.difference(manifest_lines))
    if missing_manifest:
        errors.append(
            "REPOSITORY_MANIFEST.txt: missing required release entries: "
            + ", ".join(missing_manifest)
        )

    tracked = git_tracked_files()
    if tracked is not None and manifest_lines != tracked:
        manifest_set = set(manifest_lines)
        tracked_set = set(tracked)
        missing = sorted(tracked_set - manifest_set)
        extra = sorted(manifest_set - tracked_set)
        errors.append(
            "REPOSITORY_MANIFEST.txt: does not equal git ls-files"
            + (f"; missing={missing}" if missing else "")
            + (f"; extra={extra}" if extra else "")
        )

    workflow = read(".github/workflows/release-hardening.yml")
    invocation = "python tools/check_stage7_f1_release_docs_gate.py"
    if workflow.count(invocation) != 1:
        errors.append(
            ".github/workflows/release-hardening.yml: expected exactly one F1 gate invocation"
        )

    index = read("web/index.html")
    reject(index, '<meta name="robots" content="noindex,nofollow" />', "web/index.html", errors)
    require(index, "v0.1.1 · validated patch release", "web/index.html", errors)
    require(index, 'id="citation-version">0.1.1', "web/index.html", errors)
    require(index, "five real CRSP event-study cases", "web/index.html", errors)
    require(index, 'name="google-site-verification"', "web/index.html", errors)
    reject(index, "Pre-alpha", "web/index.html", errors)

    if errors:
        print("STAGE VII-F1 RELEASE DOCUMENTATION GATE: FAIL")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("STAGE VII-F1 RELEASE DOCUMENTATION GATE: PASS")
    print(" - Stage VII/Stage VIII historical acceptance ledger: PASS")
    print(" - v0.1.0 immutable historical release record: PASS")
    print(" - v0.1.1 patch-release documentation/citation boundary: PASS")
    print(f" - repository manifest: {len(manifest_lines)} tracked paths")
    print(" - Stage VII workflow invocation: PASS")
    print(" - indexable validated patch-release boundary: PASS")


if __name__ == "__main__":
    main()
