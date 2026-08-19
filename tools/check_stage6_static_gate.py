#!/usr/bin/env python3
"""Stage VI static gate for the researcher-facing application layer."""
from __future__ import annotations

import hashlib
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


class _IndexAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.label_targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        if tag == "label" and values.get("for"):
            self.label_targets.append(str(values["for"]))



def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Stage III / IV / V scientific and browser foundations must remain valid.
for label, command in (
    ("Stage III corpus integrity", ["python", "tools/check_corpus_integrity.py"]),
    ("Stage IV numerical gate", ["python", "tools/check_stage4_gate.py"]),
    ("Stage V static gate", ["python", "tools/check_stage5_static_gate.py"]),
):
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        errors.append(f"{label} failed")

# Frozen Stage III validation + Stage IV Python core are byte-protected by a Stage VI baseline manifest.
frozen_path = ROOT / "docs/governance/stage6_frozen_scientific_tree.json"
if not frozen_path.exists():
    errors.append("Stage VI frozen scientific-tree manifest is missing")
else:
    frozen = json.loads(frozen_path.read_text())
    expected = frozen.get("files", {})
    current: dict[str, str] = {}
    for relroot in ("validation", "src/empirical_finance_lab"):
        for path in sorted((ROOT / relroot).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                rel = path.relative_to(ROOT).as_posix()
                # Stage VIII owns and closes its later real-data evidence subtree.
                if rel.startswith("validation/real_data/"):
                    continue
                current[rel] = sha256(path)
    if set(current) != set(expected):
        errors.append("Frozen scientific-tree file set changed")
    for rel, digest in expected.items():
        if current.get(rel) != digest:
            errors.append(f"Frozen scientific file changed: {rel}")

required_files = [
    "web/src/application.ts",
    "web/src/csvIntake.ts",
    "web/src/specification.ts",
    "web/src/resultsView.ts",
    "web/src/exportBundle.ts",
    "web/src/stage5Harness.ts",
    "web/src/styles.css",
    "web/tests/stage6.spec.ts",
    "docs/specifications/STAGE_VI_APPLICATION_UI.md",
    ".github/workflows/application-ui.yml",
]
for rel in required_files:
    if not (ROOT / rel).exists():
        errors.append(f"Stage VI required file missing: {rel}")

index = (ROOT / "web/index.html").read_text()
for required in (
    "Audit-First Event Study Analyzer",
    "Open a local return file",
    "Prespecify the event study",
    "Locked analysis specification",
    "Research Integrity Audit",
    "Prespecified robustness matrix",
    "Historical pseudo-event diagnostic",
    "Reproduce & cite",
    'role="status"',
):
    if required not in index:
        errors.append(f"Stage VI interface contract missing: {required}")
if "upload research data" in index.lower():
    errors.append("Stage VI UI uses misleading research-data upload language")

parser = _IndexAuditParser()
parser.feed(index)
if len(parser.ids) != len(set(parser.ids)):
    errors.append("Stage VI HTML contains duplicate element IDs")
missing_label_targets = sorted(set(parser.label_targets) - set(parser.ids))
if missing_label_targets:
    errors.append(f"Stage VI labels reference missing controls: {missing_label_targets}")

application = (ROOT / "web/src/application.ts").read_text()
stage6_browser_sources = "\n".join((ROOT / rel).read_text() for rel in (
    "web/src/application.ts",
    "web/src/csvIntake.ts",
    "web/src/specification.ts",
    "web/src/resultsView.ts",
    "web/src/exportBundle.ts",
))
for forbidden in ("localStorage", "sessionStorage", ".innerHTML", "eval(", "new Function", "XMLHttpRequest", "sendBeacon"):
    if forbidden in stage6_browser_sources:
        errors.append(f"Stage VI application contains forbidden surface: {forbidden}")
if "fetch(" in stage6_browser_sources:
    errors.append("Stage VI researcher-facing modules must not transmit/fetch research data")
if "client.run(session.normalized.csvText, session.lockedSpec)" not in application:
    errors.append("Stage VI UI does not delegate numerical execution to the validated browser client")
if "buildReproducibilityZip" not in application:
    errors.append("Stage VI reproducibility bundle integration is missing")

exporter = (ROOT / "web/src/exportBundle.ts").read_text()
for required in (
    "raw_file_sha256: context.originalUploadSha256",
    "engine_input_sha256",
    "proprietary/raw research file",
    "1980-01-01",
):
    if required not in exporter:
        errors.append(f"Stage VI reproducibility safeguard missing: {required}")

main = (ROOT / "web/src/main.ts").read_text()
if "installStage5Harness" not in main or "initializeApplication" not in main:
    errors.append("Stage VI main entry point does not preserve Stage V parity API and initialize the application")

package = json.loads((ROOT / "web/package.json").read_text())
if package.get("scripts", {}).get("test:e2e:stage6") != "playwright test tests/stage6.spec.ts":
    errors.append("Stage VI E2E script is missing or drifted")

workflow = (ROOT / ".github/workflows/application-ui.yml").read_text() if (ROOT / ".github/workflows/application-ui.yml").exists() else ""
for required in (
    "stage6-ui-${{ matrix.browser }}",
    "matrix:",
    "chromium",
    "firefox",
    "webkit",
    "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7",
    "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8",
    "python tools/check_stage6_static_gate.py",
    "npm run test:e2e:stage6 -- --project=${{ matrix.browser }}",
):
    if required not in workflow:
        errors.append(f"Stage VI CI contract missing: {required}")

# No new runtime dependency is allowed in Stage VI; the UI is framework-free by design.
package_deps = package.get("dependencies", {})
if package_deps:
    errors.append("Stage VI introduced runtime npm dependencies; v0.1 UI must remain dependency-minimal")

if errors:
    print("STAGE VI STATIC GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)
print("STAGE VI STATIC GATE: PASS")
