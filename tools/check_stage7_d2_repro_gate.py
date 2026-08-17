#!/usr/bin/env python3
"""Stage VII-D2 static gate for the privacy-preserving reproducibility round trip."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

for label, command in (
    ("Stage VII static gate", ["python", "tools/check_stage7_static_gate.py"]),
    ("Stage VII-D1 provenance gate", ["python", "tools/check_stage7_d1_provenance_gate.py"]),
):
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        errors.append(f"{label} failed")

required_files = [
    "web/src/storedZip.ts",
    "web/src/reproRoundTrip.ts",
    "web/src/exportBundle.ts",
    "web/src/exportBundle.test.ts",
    "web/tests/reproRoundTrip.ts",
    "web/tests/stage7.spec.ts",
    "web/tests-live/stage7.live.spec.ts",
    "docs/specifications/STAGE_VII_D2_REPRODUCIBILITY_ROUND_TRIP.md",
]
for rel in required_files:
    if not (ROOT / rel).is_file():
        errors.append(f"Stage VII-D2 required file missing: {rel}")

stored_zip = (ROOT / "web/src/storedZip.ts").read_text(encoding="utf-8") if (ROOT / "web/src/storedZip.ts").is_file() else ""
for required in (
    "1980-01-01",
    "ZIP_PATH_INVALID",
    "ZIP_DUPLICATE_PATH",
    "ZIP_CRC_MISMATCH",
    "ZIP_FORMAT_UNSUPPORTED",
    "ZIP_LOCAL_CENTRAL_MISMATCH",
    "ZIP_CENTRAL_BOUNDARY_MISMATCH",
):
    if required not in stored_zip:
        errors.append(f"D2 strict stored-ZIP invariant missing: {required}")
if "CompressionStream" in stored_zip or "DecompressionStream" in stored_zip:
    errors.append("D2 ZIP format must remain deterministic stored/no-compression")

round_trip = (ROOT / "web/src/reproRoundTrip.ts").read_text(encoding="utf-8") if (ROOT / "web/src/reproRoundTrip.ts").is_file() else ""
for required in (
    'EFL_REPRODUCIBILITY_BUNDLE_V2',
    '"scientific_result.json"',
    "payload_integrity",
    "tree_sha256",
    "REPRO_ORIGINAL_FILE_SHA256_MISMATCH",
    "REPRO_ENGINE_INPUT_SHA256_MISMATCH",
    "REPRO_RERUN_ANALYSIS_ID_MISMATCH",
    "REPRO_RERUN_EXECUTION_ID_MISMATCH",
    "REPRO_RERUN_BUILD_COMMIT_MISMATCH",
    "REPRO_RERUN_SCIENTIFIC_RESULT_MISMATCH",
    "normalizeMappedCsv",
    "normalized_to_original_source_row",
):
    if required not in round_trip:
        errors.append(f"D2 round-trip invariant missing: {required}")
if '"data.csv"' in round_trip or '"raw.csv"' in round_trip:
    errors.append("D2 fixed payload inventory must not embed a research-data CSV")

exporter = (ROOT / "web/src/exportBundle.ts").read_text(encoding="utf-8") if (ROOT / "web/src/exportBundle.ts").is_file() else ""
for required in (
    "ENGINE_INPUT_HASH_MISMATCH",
    '"scientific_result.json"',
    "buildPayloadIntegrity(payloadFiles)",
    "scientific_result_sha256",
    "original_local_file_required: true",
    "raw_research_data_included: false",
    "deterministic_reexport_required: true",
    "verifyReproducibilityArchive(bytes)",
    "proprietary/raw research file",
):
    if required not in exporter:
        errors.append(f"D2 exporter invariant missing: {required}")
if "coreHashes.raw_file_sha256 ?? context.engineInputSha256" in exporter:
    errors.append("D2 exporter still silently falls back between core and browser engine-input hashes")

unit_test = (ROOT / "web/src/exportBundle.test.ts").read_text(encoding="utf-8") if (ROOT / "web/src/exportBundle.test.ts").is_file() else ""
for required in (
    "REPRO_ORIGINAL_FILE_SHA256_MISMATCH",
    "ENGINE_INPUT_HASH_MISMATCH",
    "REPRO_IDENTIFIER_MISMATCH",
    "REPRO_RERUN_SCIENTIFIC_RESULT_MISMATCH",
    "../raw.csv",
    "corrupted",
):
    if required not in unit_test:
        errors.append(f"D2 negative-control coverage missing: {required}")

helper = (ROOT / "web/tests/reproRoundTrip.ts").read_text(encoding="utf-8") if (ROOT / "web/tests/reproRoundTrip.ts").is_file() else ""
for required in (
    "verifyBundle",
    "compareReproducedResult",
    "EFL_REPRODUCIBILITY_BUNDLE_V2",
    "payload_integrity.tree_sha256",
    "getLockedSpecification",
    "D2 reproduction rerun emitted a network request",
    "expect([...second.zip]).toEqual([...first.zip])",
):
    if required not in helper:
        errors.append(f"D2 browser round-trip helper invariant missing: {required}")

for rel in ("web/tests/stage7.spec.ts", "web/tests-live/stage7.live.spec.ts"):
    text = (ROOT / rel).read_text(encoding="utf-8") if (ROOT / rel).is_file() else ""
    if "await exerciseD2RoundTrip(page, EXPECTED_BUILD_COMMIT);" not in text:
        errors.append(f"D2 production/live browser gate missing round-trip execution: {rel}")

package_path = ROOT / "web/package.json"
if package_path.is_file():
    package = json.loads(package_path.read_text(encoding="utf-8"))
    expected_prebuild = "python ../tools/check_stage7_c1_security_gate.py && python ../tools/check_stage7_d2_repro_gate.py"
    if package.get("scripts", {}).get("prebuild:pages") != expected_prebuild:
        errors.append("D2 prebuild gate is not wired into every GitHub Pages candidate build")
    if package.get("dependencies"):
        errors.append("D2 introduced frontend runtime dependencies")
else:
    errors.append("web/package.json is missing")

spec = (ROOT / "docs/specifications/STAGE_VII_D2_REPRODUCIBILITY_ROUND_TRIP.md").read_text(encoding="utf-8") if (ROOT / "docs/specifications/STAGE_VII_D2_REPRODUCIBILITY_ROUND_TRIP.md").is_file() else ""
for required in (
    "ZIP plus the exact original local CSV",
    "byte-identical",
    "zero network requests",
    "must not modify",
    "Public Beta remains Stage VIII",
):
    if required not in spec:
        errors.append(f"D2 specification contract missing: {required}")

if errors:
    print("STAGE VII-D2 REPRODUCIBILITY GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print("STAGE VII-D2 REPRODUCIBILITY GATE: PASS")
