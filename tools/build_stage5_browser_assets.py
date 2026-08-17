#!/usr/bin/env python3
"""Build Stage V browser assets from the authoritative Python core and frozen fixtures.

This script packages source text; it does not create a second numerical implementation.
Runtime parity references are CPython Stage IV outcomes, not new scientific golden answers.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PUBLIC = ROOT / "web" / "public"
PUBLIC.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SRC))

from empirical_finance_lab import outcome_to_dict, run_analysis  # noqa: E402

PYODIDE_VERSION = "314.0.4"
EXPECTED_BROWSER_PYTHON = "3.14.2"
EXPECTED_BROWSER_NUMPY = "2.4.3"
EXPECTED_BROWSER_SCIPY = "1.18.0"
PARITY_FIXTURES = ("KA-003", "INF-001", "PLC-001", "ROB-001", "FM-001")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def locate_fixture(fixture_id: str) -> Path:
    manifest = json.loads((ROOT / "validation" / "manifest.json").read_text(encoding="utf-8"))
    entry = next(item for item in manifest["fixtures"] if item["fixture_id"] == fixture_id)
    return ROOT / Path(entry["files"]["data"]).parent


def build_core_bundle() -> dict[str, object]:
    package = ROOT / "src" / "empirical_finance_lab"
    files = []
    for path in sorted(package.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        files.append({
            "path": f"empirical_finance_lab/{path.name}",
            "sha256": sha256_bytes(text.encode("utf-8")),
            "text": text,
        })
    payload = "".join(f'{item["path"]}\n{item["sha256"]}\n' for item in sorted(files, key=lambda x: x["path"]))
    return {
        "schema_version": "0.1.0",
        "bundle_sha256": sha256_bytes(payload.encode("utf-8")),
        "files": files,
    }


def scientific_projection(outcome: dict[str, object]) -> dict[str, object]:
    projected = json.loads(json.dumps(outcome))
    repro = projected.get("reproducibility")
    if isinstance(repro, dict):
        repro.pop("execution_id", None)
        repro.pop("environment", None)
    return projected


def build_parity_bundle() -> dict[str, object]:
    cases = []
    for fixture_id in PARITY_FIXTURES:
        folder = locate_fixture(fixture_id)
        raw = (folder / "data.csv").read_bytes()
        spec = json.loads((folder / "specification.json").read_text(encoding="utf-8"))
        outcome = scientific_projection(outcome_to_dict(run_analysis(raw, spec)))
        cases.append({
            "fixture_id": fixture_id,
            "data_sha256": sha256_bytes(raw),
            "specification_sha256": sha256_bytes(canonical_json_bytes(spec)),
            "raw_csv_text": raw.decode("utf-8"),
            "specification": spec,
            "expected_outcome": outcome,
        })
    return {"schema_version": "0.1.0", "cases": cases}


def main() -> int:
    core = build_core_bundle()
    parity = build_parity_bundle()
    runtime_pin = {
        "schema_version": "0.1.0",
        "pyodide_version": PYODIDE_VERSION,
        "pyodide_index_url": f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/",
        "expected_browser_python": EXPECTED_BROWSER_PYTHON,
        "expected_browser_numpy": EXPECTED_BROWSER_NUMPY,
        "expected_browser_scipy": EXPECTED_BROWSER_SCIPY,
        "core_bundle_sha256": core["bundle_sha256"],
        "scientific_parity_policy": {
            "core_abs_tol": 1e-12,
            "core_rel_tol": 1e-10,
            "p_value_abs_tol": 1e-10,
            "runtime_specific_fields_excluded": [
                "reproducibility.execution_id",
                "reproducibility.environment",
            ],
        },
    }
    (PUBLIC / "efl-core.json").write_bytes(canonical_json_bytes(core) + b"\n")
    (PUBLIC / "stage5-parity-cases.json").write_bytes(canonical_json_bytes(parity) + b"\n")
    (PUBLIC / "stage5-runtime-pin.json").write_bytes(canonical_json_bytes(runtime_pin) + b"\n")
    print(f"Stage V browser assets built: {len(core['files'])} Python modules, {len(parity['cases'])} parity fixtures")
    print(f"Core bundle SHA-256: {core['bundle_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
