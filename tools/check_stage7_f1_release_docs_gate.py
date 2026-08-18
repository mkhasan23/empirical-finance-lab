from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_STAGE7_BASELINE = "08d8b1b8f5953b1e5cf93ec6a298a731757e0c87"


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
    require(root_readme, "Stage VII release hardening accepted on `main`", "README.md", errors)
    require(root_readme, ACCEPTED_STAGE7_BASELINE, "README.md", errors)
    require(root_readme, "not Public Beta", "README.md", errors)
    require(root_readme, "no formal `v0.1.0` release", "README.md", errors)
    require(root_readme, "docs/quickstart.md", "README.md", errors)
    require(root_readme, "docs/release_status.md", "README.md", errors)
    require(root_readme, "SECURITY.md", "README.md", errors)
    require(root_readme, "docs/governance/release_policy.md", "README.md", errors)
    require(
        root_readme,
        "https://mkhasan23.github.io/empirical-finance-lab/",
        "README.md",
        errors,
    )
    reject(root_readme, "Stage VII as a whole is **not yet accepted**", "README.md", errors)
    reject(root_readme, "Stage VI application-UI CI candidate", "README.md", errors)
    reject(root_readme, "Stage VI is **not accepted**", "README.md", errors)

    web_readme = read("web/README.md")
    require(web_readme, "# Stage VII accepted release-hardening browser application", "web/README.md", errors)
    require(web_readme, ACCEPTED_STAGE7_BASELINE, "web/README.md", errors)
    require(web_readme, "not Public Beta", "web/README.md", errors)
    require(web_readme, "../docs/quickstart.md", "web/README.md", errors)
    require(web_readme, "../docs/release_status.md", "web/README.md", errors)
    require(web_readme, "npm run build:pages", "web/README.md", errors)
    require(web_readme, "npm run test:e2e:stage7", "web/README.md", errors)
    reject(web_readme, "pre-release Stage VII release-hardening candidate", "web/README.md", errors)
    reject(web_readme, "# Stage VI research application UI CI candidate", "web/README.md", errors)

    changelog = read("CHANGELOG.md")
    require(changelog, "Stage VII release hardening accepted", "CHANGELOG.md", errors)
    require(changelog, ACCEPTED_STAGE7_BASELINE, "CHANGELOG.md", errors)
    require(changelog, "reproducibility ZIP round-trip", "CHANGELOG.md", errors)
    require(changelog, "not Public Beta", "CHANGELOG.md", errors)
    require(changelog, "no version-specific DOI", "CHANGELOG.md", errors)

    status = read("docs/release_status.md")
    for token in (
        "accepted Stage VII release-hardening baseline on `main`",
        ACCEPTED_STAGE7_BASELINE,
        "not Public Beta",
        "no formal `v0.1.0` release",
        "no version-specific DOI",
        "Stage VIII",
        "Stage IX",
        "repository administrator-confirmed",
        "https://mkhasan23.github.io/empirical-finance-lab/",
    ):
        require(status, token, "docs/release_status.md", errors)
    reject(status, "Stage VII as a whole is **not yet accepted**", "docs/release_status.md", errors)

    policy = read("docs/governance/release_policy.md")
    for token in (
        "Stage VII — accepted release hardening",
        "Stage VIII — Public Beta / external validation",
        "Stage IX — formal `v0.1.0` release",
        "version `0.0.0`",
        "version-specific DOI",
        "exact-commit",
    ):
        require(policy, token, "docs/governance/release_policy.md", errors)

    citation = read("CITATION.cff")
    require(citation, "version: 0.0.0", "CITATION.cff", errors)
    require(citation, "pre-release research-software project", "CITATION.cff", errors)
    for line in citation.splitlines():
        if line.strip().lower().startswith(("doi:", "identifiers:")):
            errors.append("CITATION.cff: pre-release metadata must not claim a DOI/identifier block")

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
        "docs/quickstart.md",
        "docs/release_status.md",
        "docs/specifications/STAGE_VII_F1_RELEASE_DOCUMENTATION.md",
        "examples/efl_tutorial_synthetic.csv",
        "tools/check_stage7_f1_release_docs_gate.py",
        "web/package-lock.json",
        "web/playwright.stage7.live.config.ts",
        "web/src/buildProvenance.ts",
        "web/src/reproRoundTrip.ts",
        "web/src/storedZip.ts",
        "web/tests-live/stage7.live.spec.ts",
        "web/tests/stage7.spec.ts",
    }
    missing_manifest = sorted(required_manifest_entries.difference(manifest_lines))
    if missing_manifest:
        errors.append(
            "REPOSITORY_MANIFEST.txt: missing required Stage VII entries: "
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
    require(index, '<meta name="robots" content="noindex,nofollow" />', "web/index.html", errors)
    reject(index, "Public Beta", "web/index.html", errors)

    if errors:
        print("STAGE VII-F1 RELEASE DOCUMENTATION GATE: FAIL")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("STAGE VII-F1 RELEASE DOCUMENTATION GATE: PASS")
    print(" - Stage VII accepted / Stage VIII / Stage IX status boundary: PASS")
    print(" - pre-release citation/DOI boundary: PASS")
    print(" - current onboarding/security/release links: PASS")
    print(f" - repository manifest: {len(manifest_lines)} tracked paths")
    print(" - Stage VII workflow invocation: PASS")
    print(" - accepted pre-release noindex boundary: PASS")


if __name__ == "__main__":
    main()
