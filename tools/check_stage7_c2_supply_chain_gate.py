#!/usr/bin/env python3
"""Stage VII-C2 repository-wide supply-chain governance gate."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
errors: list[str] = []

APPROVED_ACTIONS: dict[str, tuple[str, str]] = {
    "actions/checkout": ("d23441a48e516b6c34aea4fa41551a30e30af803", "v6"),
    "actions/setup-python": ("ece7cb06caefa5fff74198d8649806c4678c61a1", "v6"),
    "actions/setup-node": ("249970729cb0ef3589644e2896645e5dc5ba9c38", "v6"),
    "actions/upload-artifact": ("043fb46d1a93c77aae656e7c1c64a875d1fc6a0a", "v7"),
    "actions/download-artifact": ("3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c", "v8"),
    "actions/configure-pages": ("45bfe0192ca1faeb007ade9deae92b16b8254a0d", "v6"),
    "actions/upload-pages-artifact": ("fc324d3547104276b827a68afc52ff2a11cc49c9", "v5"),
    "actions/deploy-pages": ("cd2ce8fcbc39b97be8ca5fce6e763baed58fa128", "v5"),
}

USES_RE = re.compile(
    r"^\s*-?\s*uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})\s+#\s+(v[0-9][A-Za-z0-9_.-]*)\s*$"
)

workflow_paths = sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])
if not workflow_paths:
    errors.append("no GitHub Actions workflow files were found")

seen_actions: set[str] = set()
for path in workflow_paths:
    rel = path.relative_to(ROOT).as_posix()
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or "uses:" not in stripped:
            continue
        if "uses: ./" in stripped:
            continue
        match = USES_RE.match(raw)
        if not match:
            errors.append(f"mutable or malformed action reference: {rel}:{line_no}: {stripped}")
            continue
        action, sha, version = match.groups()
        expected = APPROVED_ACTIONS.get(action)
        if expected is None:
            errors.append(f"unapproved external action: {rel}:{line_no}: {action}")
            continue
        expected_sha, expected_version = expected
        seen_actions.add(action)
        if sha != expected_sha:
            errors.append(
                f"action SHA drift: {action} expected {expected_sha}, found {sha} in {rel}:{line_no}"
            )
        if version != expected_version:
            errors.append(
                f"action version annotation drift: {action} expected {expected_version}, found {version} in {rel}:{line_no}"
            )

missing_actions = sorted(set(APPROVED_ACTIONS) - seen_actions)
if missing_actions:
    errors.append(f"approved action set is not fully represented in workflows: {missing_actions}")

dependabot_path = ROOT / ".github" / "dependabot.yml"
if not dependabot_path.is_file():
    errors.append(".github/dependabot.yml is missing")
else:
    actual_bytes = dependabot_path.read_bytes()
    if hashlib.sha256(actual_bytes).hexdigest() != "69256c58c65cc61678c66d8b7a9a31fffd241df2b37c30c3f125835c1b651a26":
        errors.append("Dependabot policy drifted from the Stage VII-C2 controlled schedule")
    actual_dependabot = actual_bytes.decode("utf-8")
    if 'package-ecosystem: "pip"' in actual_dependabot:
        errors.append("scientific Python dependencies must not be placed on automatic Dependabot version updates")

policy_path = ROOT / "docs" / "governance" / "DEPENDENCY_UPDATE_POLICY.md"
if not policy_path.is_file():
    errors.append("dependency update policy is missing")
else:
    policy = policy_path.read_text(encoding="utf-8")
    for required in (
        "Scientific Python is not on automatic version updates",
        "full-length commit SHA",
        "Dependabot pull requests are proposals",
        "Stages III through VII",
        "Dependabot alerts",
        "Require actions to be pinned to a full-length commit SHA",
    ):
        if required not in policy:
            errors.append(f"dependency policy invariant missing: {required}")

security_path = ROOT / "SECURITY.md"
if not security_path.is_file():
    errors.append("SECURITY.md is missing")
else:
    security = security_path.read_text(encoding="utf-8")
    for required in (
        "## Supply-chain security boundary",
        "full-length commit SHA",
        "Dependabot",
        "Scientific Python",
    ):
        if required not in security:
            errors.append(f"SECURITY.md C2 invariant missing: {required}")

spec_path = ROOT / "docs" / "specifications" / "STAGE_VII_RELEASE_HARDENING.md"
if not spec_path.is_file():
    errors.append("Stage VII specification is missing")
else:
    spec = spec_path.read_text(encoding="utf-8")
    for required in (
        "## Supply-chain governance contract",
        "full-length commit SHA",
        "Dependabot",
        "Scientific Python",
        "Stages III through VII",
    ):
        if required not in spec:
            errors.append(f"Stage VII-C2 specification invariant missing: {required}")

if errors:
    print("STAGE VII-C2 SUPPLY-CHAIN GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print(
    "STAGE VII-C2 SUPPLY-CHAIN GATE: PASS "
    f"({len(workflow_paths)} workflows, {len(seen_actions)} approved actions)"
)
