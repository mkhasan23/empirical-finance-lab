#!/usr/bin/env python3
"""Stage X governed v0.1.1 patch-release integrity gate."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.1"
TAG = "v0.1.1"
RELEASE_DATE = "2026-08-19"
STAGE8_BASELINE = "a694d49df9716f9f87d359385598237363e4c3fc"
STAGE8_TREE = "621b0cafdcad3711d2aba3bef698d2e78d022144"
HISTORICAL_V010_TAG = "v0.1.0"
HISTORICAL_V010_COMMIT = "faf3dc6c5702dad3f5abd1dd15f7697fab5a5831"
OLD_INIT_SHA256 = "ae3c71e4e8c916ed3cb2d6274be93b2770baf77953944b8e381dc8aa12c02765"
V010_INIT_SHA256 = "b6fc4652ac03f40c1bbbfbcca0adf94544bc939a23cb1ac6f59b2edacb27a3fc"
V011_INIT_SHA256 = "539a4348f7d83256310cbb513e658bee227c49b31139dfc778f0d4f8c98cc680"
PATCH_TRACKED_PATH_COUNT = 226
SEARCH_CONSOLE_TOKEN = "SOTT4_QvGUdym57bgQH_r8MeDSTzjiuRMp3ZAnisJIU"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)

errors: list[str] = []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"missing required Stage X file: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, token: str, label: str) -> None:
    if token not in text:
        errors.append(f"{label}: missing {token!r}")


def reject(text: str, token: str, label: str) -> None:
    if token in text:
        errors.append(f"{label}: stale/forbidden token {token!r}")


def git_tracked_files() -> list[str] | None:
    if not (ROOT / ".git").exists():
        return None
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, stderr=subprocess.STDOUT
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"unable to read tracked-file inventory: {exc}")
        return None
    return sorted(item for item in raw.decode("utf-8").split("\0") if item)


def run_gate(command: list[str], label: str) -> None:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        errors.append(f"{label} failed")
        if proc.stdout:
            errors.append(f"{label} stdout: " + proc.stdout.strip().replace("\n", " | "))
        if proc.stderr:
            errors.append(f"{label} stderr: " + proc.stderr.strip().replace("\n", " | "))


# 1. Current version authorities.
try:
    pyproject = tomllib.loads(read("pyproject.toml"))
except tomllib.TOMLDecodeError as exc:
    errors.append(f"pyproject.toml is invalid TOML: {exc}")
    pyproject = {}

project = pyproject.get("project", {}) if isinstance(pyproject, dict) else {}
if project.get("version") != VERSION:
    errors.append(f"pyproject version must be {VERSION!r}, found {project.get('version')!r}")
if "Development Status :: 3 - Alpha" not in project.get("classifiers", []):
    errors.append("pyproject must retain Development Status :: 3 - Alpha")
project_urls = project.get("urls", {})
if project_urls.get("Release") != f"https://github.com/mkhasan23/empirical-finance-lab/releases/tag/{TAG}":
    errors.append("pyproject Release URL does not point to the governed v0.1.1 tag")

init_path = ROOT / "src/empirical_finance_lab/__init__.py"
init_text = read("src/empirical_finance_lab/__init__.py")
require(init_text, f'__version__ = "{VERSION}"', "scientific package __init__")
if init_path.is_file() and sha256(init_path) != V011_INIT_SHA256:
    errors.append("src/empirical_finance_lab/__init__.py is not the exact audited v0.1.1 metadata state")

citation = read("CITATION.cff")
for token in (
    f"version: {VERSION}",
    f"date-released: {RELEASE_DATE}",
    f"/releases/tag/{TAG}",
    "Muhammad Kamrul",
):
    require(citation, token, "CITATION.cff")
for raw in citation.splitlines():
    line = raw.strip()
    if line.lower().startswith("doi:"):
        value = line.split(":", 1)[1].strip().strip('"').strip("'")
        if not DOI_RE.fullmatch(value):
            errors.append(f"CITATION.cff contains malformed/placeholder DOI: {value!r}")

# 2. Frozen scientific tree with a closed v0.1.1 metadata exception.
frozen_text = read("docs/governance/stage6_frozen_scientific_tree.json")
if frozen_text:
    try:
        frozen = json.loads(frozen_text)
    except json.JSONDecodeError as exc:
        errors.append(f"Stage VI frozen scientific-tree manifest is invalid JSON: {exc}")
        frozen = {}
    expected = frozen.get("files", {}) if isinstance(frozen, dict) else {}
    current: dict[str, str] = {}
    for relroot in ("validation", "src/empirical_finance_lab"):
        root = ROOT / relroot
        if not root.exists():
            errors.append(f"frozen scientific root missing: {relroot}")
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                rel = path.relative_to(ROOT).as_posix()
                if rel.startswith("validation/real_data/"):
                    continue
                current[rel] = sha256(path)

    if set(current) != set(expected):
        missing = sorted(set(expected) - set(current))
        extra = sorted(set(current) - set(expected))
        errors.append(
            "frozen Stage III/IV file set changed"
            + (f"; missing={missing}" if missing else "")
            + (f"; extra={extra}" if extra else "")
        )

    for rel, digest in expected.items():
        actual = current.get(rel)
        if rel == "src/empirical_finance_lab/__init__.py":
            if digest != OLD_INIT_SHA256:
                errors.append("frozen manifest's accepted pre-release __init__.py identity drifted")
            if actual != V011_INIT_SHA256:
                errors.append("current __init__.py does not match the exact closed v0.1.1 metadata state")
        elif actual != digest:
            errors.append(f"frozen scientific file changed: {rel}")

stage6_gate = read("tools/check_stage6_static_gate.py")
for token in (
    OLD_INIT_SHA256,
    V010_INIT_SHA256,
    V011_INIT_SHA256,
    "allowed_release_metadata_hashes",
    'rel == "src/empirical_finance_lab/__init__.py"',
):
    require(stage6_gate, token, "Stage VI closed release-metadata exception")
if 'rel.startswith("src/empirical_finance_lab/")' in stage6_gate:
    errors.append("Stage VI gate contains a broad scientific-package path exemption")

# 3. Historical v0.1.0 and Stage VIII authority must remain green.
run_gate(["python", "tools/check_stage9_release_gate.py"], "Stage IX historical v0.1.0 gate")
run_gate(["python", "tools/check_stage8_real_data_gate.py"], "Stage VIII public real-data evidence/licensing gate")

stage8_doc = read("docs/STAGE_VIII_REAL_DATA_VALIDATION.md")
for token in (
    STAGE8_BASELINE,
    STAGE8_TREE,
    "2.7755575615628914e-16",
    "every permutation extreme count matched exactly",
    "not included in this repository",
):
    require(stage8_doc, token, "Stage VIII validation record")

# 4. Browser/runtime/reproducibility patch-release state.
index = read("web/index.html")
for token in (
    "v0.1.1 · validated patch release",
    'id="citation-version">0.1.1',
    "five real CRSP event-study cases",
    "Significant CAR ≠ causal effect established",
    f'name="google-site-verification" content="{SEARCH_CONSOLE_TOKEN}"',
    'rel="canonical" href="https://mkhasan23.github.io/empirical-finance-lab/"',
    "Muhammad Kamrul Hasan",
    "/releases/tag/v0.1.1",
):
    require(index, token, "web/index.html")
reject(index, 'content="noindex,nofollow"', "web/index.html")
reject(index, "Pre-alpha", "web/index.html")
require(index, 'id="estimation-start" type="number" value="-250"', "web/index.html")
require(index, 'id="estimation-end" type="number" value="-30"', "web/index.html")

for rel in (
    "web/tests/stage5.spec.ts",
    "web/tests/stage7.spec.ts",
    "web/tests-live/stage7.live.spec.ts",
):
    text = read(rel)
    require(text, 'expect(runtime.efl_version).toBe("0.1.1")', rel)
    reject(text, 'expect(runtime.efl_version).toBe("0.1.0")', rel)

csv_intake = read("web/src/csvIntake.ts")
for token in (
    '"YYYY/MM/DD"',
    '"YYYYMMDD"',
    '"MM/DD/YYYY"',
    '"DD/MM/YYYY"',
    "DlyCalDt",
    "DlyRet",
    "vwretd",
    "explicitAmbiguousFormatSelection",
):
    require(csv_intake, token, "web/src/csvIntake.ts")

specification = read("web/src/specification.ts")
for token in (
    "date_canonicalization",
    "requested_format",
    "detected_source_formats",
    "transformed_rows",
    "explicit_ambiguous_format_selection",
):
    require(specification, token, "web/src/specification.ts")
require(specification, 'estimationWindow: { start: -250, end: -30 }', "web/src/specification.ts")

exporter = read("web/src/exportBundle.ts")
for token in (
    'const releaseTag = releaseVersion === "UNAVAILABLE" ? "UNAVAILABLE" : `v${releaseVersion}`',
    '`https://github.com/mkhasan23/empirical-finance-lab/releases/tag/${releaseTag}`',
    'software_version: coreRepro.software_version ?? "UNAVAILABLE"',
    "No version-specific DOI is claimed unless",
):
    require(exporter, token, "web/src/exportBundle.ts")
reject(exporter, '"Formal release tag: v0.1.0."', "web/src/exportBundle.ts")
reject(exporter, "/releases/tag/v0.1.0", "web/src/exportBundle.ts")

package_text = read("web/package.json")
try:
    package = json.loads(package_text) if package_text else {}
except json.JSONDecodeError as exc:
    errors.append(f"web/package.json invalid JSON: {exc}")
    package = {}
if package.get("private") is not True or package.get("version") != "0.0.0":
    errors.append("web/package.json must remain the private internal 0.0.0 workspace package")

# 5. Public claims, docs, privacy, and release history.
readme = read("README.md")
for token in (
    "v0.1.1 validated patch release line",
    "v0.1.1 interoperability and usability patch",
    HISTORICAL_V010_TAG,
    HISTORICAL_V010_COMMIT,
    "five heterogeneous real CRSP event-study cases",
    "2.7755575615628914e-16",
    "not a universal claim",
    "Researcher feedback",
    "[-250,-30]",
    "[-256,-46]",
):
    require(readme, token, "README.md")
for forbidden in ("validated by ChatGPT", "CRSP-certified", "WRDS-certified"):
    reject(readme, forbidden, "README.md")

status = read("docs/release_status.md")
for token in (
    "v0.1.1 validated patch release line",
    "Stage X patch-release contract",
    HISTORICAL_V010_COMMIT,
    "Intended patch release tag: `v0.1.1`",
    "[-250,-30]",
    "[-256,-46]",
):
    require(status, token, "docs/release_status.md")

policy = read("docs/governance/release_policy.md")
for token in (
    "Stage IX — immutable historical `v0.1.0` release",
    "Stage X — governed `v0.1.1` patch release",
    "tag == software version",
    "private frontend workspace package version `0.0.0`",
):
    require(policy, token, "release policy")

feedback = read(".github/ISSUE_TEMPLATE/researcher_feedback.yml")
for token in (
    "Researcher feedback",
    "Do not attach proprietary, licensed, confidential, or observation-level research data",
    "minimal synthetic example",
    "EFL build commit",
    "Public-data confirmation",
):
    require(feedback, token, "Researcher feedback issue form")

# 6. Repository inventory.
manifest_lines = [
    line.strip()
    for line in read("REPOSITORY_MANIFEST.txt").splitlines()
    if line.strip()
]
if manifest_lines != sorted(manifest_lines):
    errors.append("REPOSITORY_MANIFEST.txt is not lexicographically sorted")
if len(manifest_lines) != len(set(manifest_lines)):
    errors.append("REPOSITORY_MANIFEST.txt contains duplicate paths")
if len(manifest_lines) != PATCH_TRACKED_PATH_COUNT:
    errors.append(
        f"v0.1.1 governed repository inventory must contain exactly "
        f"{PATCH_TRACKED_PATH_COUNT} tracked paths before tagging; found {len(manifest_lines)}"
    )
for required in (
    ".github/ISSUE_TEMPLATE/researcher_feedback.yml",
    ".github/workflows/formal-release.yml",
    ".github/workflows/patch-release.yml",
    "docs/specifications/STAGE_IX_FORMAL_RELEASE.md",
    "docs/specifications/STAGE_X_V0.1.1_PATCH_RELEASE.md",
    "tools/check_stage9_release_gate.py",
    "tools/check_stage10_patch_release_gate.py",
    "web/public/sitemap.xml",
):
    if required not in manifest_lines:
        errors.append(f"REPOSITORY_MANIFEST.txt missing governed path: {required}")

tracked = git_tracked_files()
if tracked is not None and manifest_lines != tracked:
    missing = sorted(set(tracked) - set(manifest_lines))
    extra = sorted(set(manifest_lines) - set(tracked))
    errors.append(
        "REPOSITORY_MANIFEST.txt does not equal git ls-files"
        + (f"; missing={missing}" if missing else "")
        + (f"; extra={extra}" if extra else "")
    )

# 7. Stage X workflow and tag contract.
workflow = read(".github/workflows/patch-release.yml")
for token in (
    "name: Stage X v0.1.1 patch release",
    "push:",
    "pull_request:",
    "workflow_dispatch:",
    "stage-v0.1.1-usability-patch",
    "tags:",
    "- 'v0.1.1'",
    "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6",
    "fetch-depth: 0",
    "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6",
    "python-version: '3.13'",
    "python tools/check_stage10_patch_release_gate.py",
    "stage10-required",
):
    require(workflow, token, "Stage X workflow")
if workflow.count("python tools/check_stage10_patch_release_gate.py") != 1:
    errors.append("Stage X workflow must invoke the patch-release gate exactly once")

action_pattern = re.compile(r"^\s*-?\s*uses:\s*([^\s@]+)@([^\s#]+)", re.MULTILINE)
approved = {
    "actions/checkout": "d23441a48e516b6c34aea4fa41551a30e30af803",
    "actions/setup-python": "ece7cb06caefa5fff74198d8649806c4678c61a1",
}
for action, ref in action_pattern.findall(workflow):
    if action.startswith("./"):
        continue
    if approved.get(action) != ref:
        errors.append(f"Stage X workflow uses unapproved/mutable action reference: {action}@{ref}")

ref_type = os.environ.get("GITHUB_REF_TYPE", "").strip()
ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
if ref_type == "tag":
    if ref_name != TAG:
        errors.append(f"patch-release tag mismatch: expected {TAG!r}, observed {ref_name!r}")
    if not (ROOT / ".git").exists():
        errors.append("tag-specific Stage X gate requires a Git checkout with full history")
    else:
        try:
            tag_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip()
            main_commit = subprocess.check_output(
                ["git", "rev-parse", "refs/remotes/origin/main"], cwd=ROOT, text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"unable to verify immutable v0.1.1 tag target against origin/main: {exc}")
        else:
            if not SHA40.fullmatch(tag_commit) or not SHA40.fullmatch(main_commit):
                errors.append("v0.1.1 tag/main commit identity is malformed")
            elif tag_commit != main_commit:
                errors.append(
                    f"immutable {TAG} tag does not target the exact governed main commit: "
                    f"tag={tag_commit} main={main_commit}"
                )

if errors:
    print("STAGE X V0.1.1 PATCH RELEASE GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print("STAGE X V0.1.1 PATCH RELEASE GATE: PASS")
print(f" - software version: {VERSION}")
print(f" - intended patch release tag: {TAG}")
print(f" - historical v0.1.0 authority: PASS ({HISTORICAL_V010_COMMIT})")
print(" - Stage III/IV frozen scientific authority: PASS")
print(" - exact v0.1.1 __init__.py metadata exception: PASS")
print(" - Stage VIII public real-data/licensing evidence: PASS")
print(" - date interoperability/provenance contract: PASS")
print(" - dynamic release citation/discoverability contract: PASS")
print(" - public feedback/privacy boundary: PASS")
print(f" - repository manifest: {len(manifest_lines)} tracked paths")
if ref_type == "tag":
    print(f" - immutable tag identity: PASS ({ref_name}; exact origin/main target)")
else:
    print(f" - candidate state: PASS; immutable {TAG} tag still required after exact-main validation")
