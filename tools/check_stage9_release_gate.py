#!/usr/bin/env python3
"""Stage IX historical v0.1.0 release-integrity gate.

The immutable v0.1.0 tag is historical authority. Later patch lines may advance
the current software version, but they must not move or redefine v0.1.0.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = "v0.1.0"
EXPECTED_TAG_COMMIT = "faf3dc6c5702dad3f5abd1dd15f7697fab5a5831"
RELEASE_VERSION = "0.1.0"
RELEASE_DATE = "2026-08-19"
RELEASE_INIT_SHA256 = "b6fc4652ac03f40c1bbbfbcca0adf94544bc939a23cb1ac6f59b2edacb27a3fc"
STAGE8_BASELINE = "a694d49df9716f9f87d359385598237363e4c3fc"
STAGE8_TREE = "621b0cafdcad3711d2aba3bef698d2e78d022144"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

errors: list[str] = []


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"missing required historical-release governance file: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, token: str, label: str) -> None:
    if token not in text:
        errors.append(f"{label}: missing {token!r}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_output(args: list[str], *, binary: bool = False) -> str | bytes | None:
    if not (ROOT / ".git").exists():
        return None
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            stderr=subprocess.STDOUT,
            text=not binary,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"git {' '.join(args)} failed: {exc}")
        return None


def tagged_text(path: str) -> str | None:
    value = git_output(["show", f"{TAG}:{path}"])
    return value if isinstance(value, str) else None


# 1. Historical tag identity and exact release metadata.
tag_commit_value = git_output(["rev-parse", f"refs/tags/{TAG}^{{commit}}"])
if isinstance(tag_commit_value, str):
    tag_commit = tag_commit_value.strip()
    if not SHA40.fullmatch(tag_commit):
        errors.append(f"historical {TAG} target is malformed: {tag_commit!r}")
    elif tag_commit != EXPECTED_TAG_COMMIT:
        errors.append(
            f"historical {TAG} moved: expected {EXPECTED_TAG_COMMIT}, observed {tag_commit}"
        )

    tagged_pyproject = tagged_text("pyproject.toml") or ""
    tagged_citation = tagged_text("CITATION.cff") or ""
    tagged_init = git_output(["show", f"{TAG}:src/empirical_finance_lab/__init__.py"], binary=True)
    tagged_readme = tagged_text("README.md") or ""

    require(tagged_pyproject, 'version = "0.1.0"', f"{TAG} pyproject")
    require(tagged_pyproject, "/releases/tag/v0.1.0", f"{TAG} pyproject")
    require(tagged_citation, "version: 0.1.0", f"{TAG} CITATION.cff")
    require(tagged_citation, "date-released: 2026-08-19", f"{TAG} CITATION.cff")
    require(tagged_citation, "/releases/tag/v0.1.0", f"{TAG} CITATION.cff")
    require(tagged_readme, "v0.1.0 validated release", f"{TAG} README")
    if isinstance(tagged_init, bytes) and sha256_bytes(tagged_init) != RELEASE_INIT_SHA256:
        errors.append(
            f"historical {TAG} __init__.py bytes drifted from the accepted release identity"
        )
else:
    # Source archives without .git cannot prove tag identity; CI checkout with full history does.
    print("STAGE IX NOTE: no Git checkout available; immutable tag identity deferred to CI.")

# 2. Current repository must continue to preserve the historical record.
current_readme = read("README.md")
for token in (
    TAG,
    EXPECTED_TAG_COMMIT,
    STAGE8_BASELINE,
    STAGE8_TREE,
):
    require(current_readme, token, "current README historical record")

stage6_gate = read("tools/check_stage6_static_gate.py")
for token in (
    RELEASE_INIT_SHA256,
    "allowed_release_metadata_hashes",
    'rel == "src/empirical_finance_lab/__init__.py"',
):
    require(stage6_gate, token, "Stage VI closed release-metadata exception")

stage8_doc = read("docs/STAGE_VIII_REAL_DATA_VALIDATION.md")
for token in (
    STAGE8_BASELINE,
    STAGE8_TREE,
    "2.7755575615628914e-16",
    "not included in this repository",
):
    require(stage8_doc, token, "Stage VIII validation record")

# 3. Current Stage IX workflow remains immutable-action pinned and scoped to v0.1.0.
workflow = read(".github/workflows/formal-release.yml")
for token in (
    "name: Stage IX formal release",
    "pull_request:",
    "workflow_dispatch:",
    "tags:",
    "- 'v0.1.0'",
    "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6",
    "fetch-depth: 0",
    "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6",
    "python-version: '3.13'",
    "python tools/check_stage9_release_gate.py",
    "stage9-required",
):
    require(workflow, token, "Stage IX workflow")

# 4. If this exact historical tag is being re-verified, HEAD must be the accepted commit.
import os
ref_type = os.environ.get("GITHUB_REF_TYPE", "").strip()
ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
if ref_type == "tag" and ref_name == TAG:
    head_value = git_output(["rev-parse", "HEAD"])
    if isinstance(head_value, str) and head_value.strip() != EXPECTED_TAG_COMMIT:
        errors.append(
            f"{TAG} workflow HEAD is not the accepted historical release commit: "
            f"{head_value.strip()}"
        )

if errors:
    print("STAGE IX HISTORICAL V0.1.0 RELEASE GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print("STAGE IX HISTORICAL V0.1.0 RELEASE GATE: PASS")
print(f" - immutable historical tag: {TAG}")
print(f" - accepted tag commit: {EXPECTED_TAG_COMMIT}")
print(" - v0.1.0 tagged package/citation identity: PASS")
print(" - current Stage VI closed metadata exception retains v0.1.0: PASS")
print(" - Stage VIII scientific authority retained: PASS")
