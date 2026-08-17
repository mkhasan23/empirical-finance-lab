#!/usr/bin/env python3
"""Stage VII-D1 build-provenance authority gate."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(rel: str, needles: tuple[str, ...]) -> str:
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"missing D1 file: {rel}")
        return ""
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"D1 invariant missing in {rel}: {needle}")
    return text


provenance = require(
    "web/src/buildProvenance.ts",
    (
        "__EFL_BUILD_COMMIT__",
        "__EFL_BUILD_MODE__",
        "__EFL_BUILD_SOURCE__",
        'build_commit: validateBuildCommit(__EFL_BUILD_COMMIT__)',
        '/^[0-9a-f]{40}$/',
    ),
)

vite = require(
    "web/vite.config.ts",
    (
        'process.env.EFL_BUILD_COMMIT ?? "UNSET"',
        'mode === "github-pages"',
        "GitHub Pages candidates require EFL_BUILD_COMMIT",
        "__EFL_BUILD_COMMIT__",
        "__EFL_BUILD_MODE__",
        "__EFL_BUILD_SOURCE__",
        'process.env.GITHUB_ACTIONS === "true" ? "github-actions" : "local"',
    ),
)

protocol = require(
    "web/src/protocol.ts",
    (
        "build_commit: string",
        "build_mode: string",
        "build_source: string",
    ),
)

worker = require(
    "web/src/eflWorker.ts",
    (
        'import { BUILD_PROVENANCE } from "./buildProvenance"',
        'os.environ[\'EFL_BUILD_COMMIT\'] = efl_build_commit',
        '"build_commit": os.environ.get("EFL_BUILD_COMMIT", "UNSET")',
        "BUILD_COMMIT_RUNTIME_MISMATCH",
        "build_mode: BUILD_PROVENANCE.build_mode",
        "build_source: BUILD_PROVENANCE.build_source",
    ),
)

exporter = require(
    "web/src/exportBundle.ts",
    (
        "BUILD_PROVENANCE_COMMIT_MISMATCH",
        "BUILD_PROVENANCE_PAGES_COMMIT_INVALID",
        "build_provenance: buildProvenance",
        "Build commit:",
    ),
)

unit = require(
    "web/src/exportBundle.test.ts",
    (
        "records one consistent build provenance authority across export metadata",
        "rejects disagreement between browser and scientific-core build commits",
        "BUILD_PROVENANCE_COMMIT_MISMATCH",
    ),
)

for rel in ("web/tests/stage7.spec.ts", "web/tests-live/stage7.live.spec.ts"):
    require(
        rel,
        (
            "EXPECTED_BUILD_COMMIT = process.env.EFL_BUILD_COMMIT",
            'expect(runtime.build_commit).toBe(EXPECTED_BUILD_COMMIT)',
            'expect(runtime.build_mode).toBe("github-pages")',
            'expect(runtime.build_source).toBe("github-actions")',
            "coreEnvironment.build_commit",
            "repro.execution_id",
        ),
    )

workflow = require(
    ".github/workflows/release-hardening.yml",
    (
        'EFL_BUILD_COMMIT: ${{ github.sha }}',
        'test "$(git rev-parse HEAD)" = "$EFL_BUILD_COMMIT"',
        '[[ "$EFL_BUILD_COMMIT" =~ ^[0-9a-f]{40}$ ]]',
        "python tools/check_stage7_d1_provenance_gate.py",
        "npm run build:pages",
        "npm run test:e2e:stage7",
        "npm run test:e2e:stage7:live",
    ),
)

reporting = require(
    "src/empirical_finance_lab/reporting.py",
    (
        'build_commit or os.environ.get("EFL_BUILD_COMMIT", "UNSET")',
        'build_commit = str(runtime.get("build_commit", "UNSET"))',
        "+ build_commit.encode(\"utf-8\")",
    ),
)

parity = require(
    "web/src/parity.ts",
    (
        "delete r.execution_id",
        "delete r.environment",
    ),
)

spec = require(
    "docs/specifications/STAGE_VII_RELEASE_HARDENING.md",
    (
        "## Build provenance authority contract",
        "EFL_BUILD_COMMIT",
        "exact checked-out Git commit",
        "AnalysisID",
        "ExecutionID",
        "no timestamps",
        "no workflow-run identifiers",
    ),
)

for text, label in ((provenance, "buildProvenance.ts"), (vite, "vite.config.ts")):
    for forbidden in ("GITHUB_RUN_ID", "GITHUB_RUN_NUMBER", "Date.now", "new Date("):
        if forbidden in text:
            errors.append(f"nondeterministic build provenance surface in {label}: {forbidden}")


if errors:
    print("STAGE VII-D1 BUILD PROVENANCE GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print("STAGE VII-D1 BUILD PROVENANCE GATE: PASS")
