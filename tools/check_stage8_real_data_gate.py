#!/usr/bin/env python3
"""Stage VIII public real-data evidence integrity/license-boundary gate.

This gate intentionally does not reconstruct licensed CRSP observations. It verifies
public evidence identity, internal hashing/parity consistency, and that known private
Stage VIII artifacts have not been committed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "validation" / "real_data"

EFL_BASELINE_COMMIT = "ebbb1d0629f9fd1a128ff3d09f1494bbcaf1fb39"
RAW_CRSP_SHA256 = "68d365faad1290ac01d9d07b64cdb037375d234aa5298e25b94897989d2a1557"
EXPECTED_CASES = {"MSFT", "PG", "NVDA", "WMT", "KO"}
ABS_TOL = 1e-12
REL_TOL = 1e-10
P_TOL = 1e-10
MAX_OBSERVED_DELTA = 2.7755575615628914e-16

# Exact private artifacts known from the authorized local validation run. If any file
# in the repository has one of these SHA-256 values, the gate blocks the commit.
PRIVATE_ARTIFACT_HASHES = {
    RAW_CRSP_SHA256,
    "1ba8d4c223e68153e7a8ca2c857054c1bcddfb98a6d863022202468f90c3f48e",  # MSFT input
    "11a52d965665982804b4e1504763db4f8f79f6dcb720bf15aecb06995da86ca7",  # PG input
    "b1e2e319452fca14a1afce86a5d84d81943972079cac23afddf90ec9c246d278",  # NVDA input
    "db99fbff850941d1839951ec2e47b16cfa7f7caf9966338d7f5afb484f1bc319",  # WMT input
    "04c365ebdd277659ca0df745d3d17bb4b43c193cd4ff9a44c1218cd72a61e930",  # KO input
}

EXPECTED_PUBLIC_FILE_SHA256 = {
    "validation/real_data/stage8c_manifest.json": "7081c3c64afbbc7caffd62983f07522a6ff8d70c2e2488da2e9519e7d76492d8",
    "validation/real_data/stage8c_parity_results.json": "2166705525a6ce4c5b263ea96d5341f8c107106ba36dabee582cba534ef6a981",
    "validation/real_data/stage8c_parity_results.csv": "9500e87f47b0ec77fcbb84e6924f4e2568d49b6e72935e2af88fb52091a5b3b9",
    "validation/real_data/specifications/efl_stage8_msft_specification.json": "5c8a2e0d5805dd6198be852d2ac12a2bb49367e5f2210d986933f8b030adc7a8",
    "validation/real_data/specifications/efl_stage8_pg_specification.json": "394574d6c04146681c977bdefca31eaf5a82075aeba6d9b36fbb8f3f0023da4d",
    "validation/real_data/specifications/efl_stage8_nvda_specification.json": "1e907f83b2e9abf6dd6b95263f7a7592fcdc79c1b55374f11c57f646b1f9a457",
    "validation/real_data/specifications/efl_stage8_wmt_specification.json": "061b839088a460ec81b40592c0e713cfd98b82d44c49e3fb37b99735c6e3cf1c",
    "validation/real_data/specifications/efl_stage8_ko_specification.json": "b02a5f71767383938dfaaa8c8785322deec6f70b2d18f46bf62f089f1c6f5c9b",
}

EXPECTED_EVENT_CONTRACT = {
    "MSFT": ("2022-01-18", "2022-01-18", "during_or_before_market", 224),
    "PG": ("2024-04-09", "2024-04-10", "after_market", 951),
    "NVDA": ("2024-05-22", "2024-05-23", "after_market", 18),
    "WMT": ("2024-11-19", "2024-11-19", "during_or_before_market", 105),
    "KO": ("2025-12-10", "2025-12-11", "after_market", 785),
}

errors: list[str] = []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def efl_spec_to_dict(spec: dict[str, Any]) -> dict[str, Any]:
    """Mirror AnalysisSpecification.to_dict() for the frozen Stage VIII specs.

    The EFL schema intentionally omits robustness_models when the tuple is empty,
    even if an empty array was supplied in the source mapping.
    """
    out = dict(spec)
    if not out.get("robustness_models"):
        out.pop("robustness_models", None)
    return out


def numeric_close(a: float, b: float, *, p_value: bool = False) -> bool:
    tol = P_TOL if p_value else ABS_TOL + REL_TOL * abs(b)
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol


# 1. Exact identities of the public evidence/specification files.
for rel, expected_hash in EXPECTED_PUBLIC_FILE_SHA256.items():
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"missing public Stage VIII evidence file: {rel}")
        continue
    actual_hash = sha256(path)
    if actual_hash != expected_hash:
        errors.append(f"SHA-256 mismatch for public Stage VIII evidence file: {rel}")

manifest_path = EVIDENCE / "stage8c_manifest.json"
results_json_path = EVIDENCE / "stage8c_parity_results.json"
results_csv_path = EVIDENCE / "stage8c_parity_results.csv"
if not all(path.is_file() for path in (manifest_path, results_json_path, results_csv_path)):
    errors.append("Stage VIII public evidence set is incomplete")
else:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = json.loads(results_json_path.read_text(encoding="utf-8"))

    # 2. Frozen software/data/design anchors.
    if manifest.get("stage") != "VIII-C":
        errors.append("manifest stage must remain VIII-C")
    if manifest.get("efl_commit") != EFL_BASELINE_COMMIT:
        errors.append("manifest EFL baseline commit drifted")
    raw_source = manifest.get("raw_crsp_source", {})
    if raw_source.get("sha256") != RAW_CRSP_SHA256:
        errors.append("manifest raw CRSP SHA-256 anchor drifted")
    if raw_source.get("included_in_public_package") is not False:
        errors.append("manifest must state raw CRSP source is excluded from public package")

    if results.get("stage") != "VIII-C" or results.get("status") != "PASS":
        errors.append("parity results must remain Stage VIII-C PASS")
    if results.get("efl_commit") != EFL_BASELINE_COMMIT:
        errors.append("parity results EFL baseline commit drifted")
    if results.get("raw_crsp_source_sha256") != RAW_CRSP_SHA256:
        errors.append("parity results raw CRSP SHA-256 anchor drifted")
    tol = results.get("parity_tolerance", {})
    if tol != {"ABS_TOL": ABS_TOL, "P_TOL": P_TOL, "REL_TOL": REL_TOL}:
        errors.append("Stage VIII parity tolerance drifted")
    max_delta = results.get("max_abs_numeric_delta")
    if not isinstance(max_delta, (int, float)) or not math.isclose(float(max_delta), MAX_OBSERVED_DELTA, rel_tol=0.0, abs_tol=0.0):
        errors.append("recorded maximum Stage VIII numerical delta drifted")

    frozen_spec = results.get("specification", {})
    expected_spec = {
        "direction": "two_sided",
        "estimation_window": [-256, -46],
        "event_window": [-1, 1],
        "model": "market_model",
        "permutation_B": 1000,
        "placebo_enabled": False,
        "return_units": "decimal",
        "robustness_models": [],
        "robustness_windows": [],
        "seed": 20260817,
    }
    if frozen_spec != expected_spec:
        errors.append("Stage VIII frozen analysis design drifted")

    derived_inputs = manifest.get("derived_inputs", {})
    cases = results.get("cases", {})
    if set(derived_inputs) != EXPECTED_CASES:
        errors.append(f"manifest case set mismatch: {sorted(derived_inputs)}")
    if set(cases) != EXPECTED_CASES:
        errors.append(f"parity-results case set mismatch: {sorted(cases)}")

    # 3. Specifications, canonical spec hashes, analysis IDs and numerical parity.
    for ticker in sorted(EXPECTED_CASES):
        if ticker not in derived_inputs or ticker not in cases:
            continue
        item = derived_inputs[ticker]
        case = cases[ticker]
        cal_date, eff_date, timing, extreme_count = EXPECTED_EVENT_CONTRACT[ticker]

        if case.get("calendar_event_date") != cal_date:
            errors.append(f"{ticker}: calendar event date drifted")
        if case.get("effective_event_date") != eff_date:
            errors.append(f"{ticker}: effective event date drifted")
        if case.get("event_timing") != timing:
            errors.append(f"{ticker}: event timing classification drifted")

        spec_rel = f"validation/real_data/specifications/efl_stage8_{ticker.lower()}_specification.json"
        spec_path = ROOT / spec_rel
        if not spec_path.is_file():
            continue
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        if spec.get("calendar_event_date") != cal_date or spec.get("effective_event_date") != eff_date:
            errors.append(f"{ticker}: specification event dates do not match case registry")
        if spec.get("event_timing") != timing:
            errors.append(f"{ticker}: specification event timing does not match case registry")
        if spec.get("estimation_window") != {"start": -256, "end": -46}:
            errors.append(f"{ticker}: estimation window drifted")
        if spec.get("event_window") != {"start": -1, "end": 1}:
            errors.append(f"{ticker}: event window drifted")
        if spec.get("model") != "market_model" or spec.get("return_units") != "decimal" or spec.get("locked") is not True:
            errors.append(f"{ticker}: core locked specification drifted")
        if spec.get("inference") != {"direction": "two_sided", "permutation_B": 1000, "seed": 20260817}:
            errors.append(f"{ticker}: inference specification drifted")
        if spec.get("placebo") != {"enabled": False} or spec.get("robustness_models") != [] or spec.get("robustness_windows") != []:
            errors.append(f"{ticker}: Stage VIII-C secondary-analysis settings drifted")

        # EFL specification hash is SHA-256 of canonical JSON AnalysisSpecification.to_dict().
        spec_hash = hashlib.sha256(canonical_json_bytes(efl_spec_to_dict(spec))).hexdigest()
        if spec_hash != item.get("specification_sha256"):
            errors.append(f"{ticker}: canonical specification SHA-256 mismatch")
        if sha256(spec_path) != item.get("json_file_sha256"):
            errors.append(f"{ticker}: specification file SHA-256 mismatch against manifest")

        canonical_hash = item.get("canonical_data_sha256")
        analysis_id = item.get("analysis_id")
        if not isinstance(canonical_hash, str) or len(canonical_hash) != 64:
            errors.append(f"{ticker}: invalid canonical data hash")
        else:
            recomputed_analysis_id = hashlib.sha256((canonical_hash + spec_hash).encode("ascii")).hexdigest()
            if recomputed_analysis_id != analysis_id:
                errors.append(f"{ticker}: analysis ID is inconsistent with canonical-data/specification hashes")
        if case.get("hashes", {}).get("analysis_id") != analysis_id:
            errors.append(f"{ticker}: results/manifest analysis ID mismatch")
        if case.get("hashes", {}).get("canonical_data_sha256") != canonical_hash:
            errors.append(f"{ticker}: results/manifest canonical-data hash mismatch")
        if case.get("hashes", {}).get("raw_file_sha256") != item.get("raw_file_sha256"):
            errors.append(f"{ticker}: results/manifest derived-input hash mismatch")

        comparisons = case.get("comparisons", {})
        required_comparisons = {
            "alpha", "beta", "residual_scale", "r_squared", "ar_m1", "ar_0", "ar_p1", "car",
            "classical_se", "classical_t", "classical_p", "permutation_t_car", "permutation_p",
            "permutation_extreme_count",
        }
        if not required_comparisons.issubset(comparisons):
            errors.append(f"{ticker}: missing required parity comparison fields")
        for field in required_comparisons:
            comp = comparisons.get(field)
            if not isinstance(comp, dict):
                continue
            if comp.get("pass") is not True:
                errors.append(f"{ticker}: recorded parity failure at {field}")
            if field == "permutation_extreme_count":
                if comp.get("efl_core") != extreme_count or comp.get("external") != extreme_count or comp.get("delta") != 0:
                    errors.append(f"{ticker}: permutation extreme count mismatch")
                continue
            try:
                a = float(comp["efl_core"])
                b = float(comp["external"])
            except (KeyError, TypeError, ValueError):
                errors.append(f"{ticker}: invalid numerical parity record at {field}")
                continue
            if not numeric_close(a, b, p_value=field.endswith("_p")):
                errors.append(f"{ticker}: parity tolerance exceeded at {field}")

        core = case.get("efl_core_result", {})
        external = case.get("independent_external_result", {})
        if core.get("est_n") != 211 or core.get("event_n") != 3:
            errors.append(f"{ticker}: EFL estimation/event observation count drifted")
        if core.get("perm_ge") != extreme_count or external.get("perm_ge") != extreme_count:
            errors.append(f"{ticker}: permutation extreme-count summary drifted")

    # 4. Cross-check compact CSV against JSON for key scientific quantities.
    with results_csv_path.open(newline="", encoding="utf-8") as handle:
        rows = {row["ticker"]: row for row in csv.DictReader(handle)}
    if set(rows) != EXPECTED_CASES:
        errors.append(f"Stage VIII CSV case set mismatch: {sorted(rows)}")
    for ticker in sorted(EXPECTED_CASES & set(rows) & set(cases)):
        row = rows[ticker]
        case = cases[ticker]
        core = case["efl_core_result"]
        if int(row["estimation_n"]) != 211 or int(row["event_n"]) != 3:
            errors.append(f"{ticker}: CSV observation counts drifted")
        for csv_field, json_field, p_field in (
            ("alpha", "alpha", False),
            ("beta", "beta", False),
            ("car", "car", False),
            ("classical_t", "classical_t", False),
            ("classical_p", "classical_p", True),
            ("permutation_p", "perm_p", True),
        ):
            if not numeric_close(float(row[csv_field]), float(core[json_field]), p_value=p_field):
                errors.append(f"{ticker}: CSV/JSON mismatch at {csv_field}")
        if int(row["permutation_extreme_count"]) != int(core["perm_ge"]):
            errors.append(f"{ticker}: CSV/JSON permutation extreme-count mismatch")
        if row.get("parity_pass") != "True":
            errors.append(f"{ticker}: CSV parity_pass must remain True")

    # 5. Manifest result-file hashes must match the actual result files.
    manifest_result_files = manifest.get("result_files", {})
    if manifest_result_files.get("stage8c_parity_results.json") != sha256(results_json_path):
        errors.append("manifest hash mismatch for stage8c_parity_results.json")
    if manifest_result_files.get("stage8c_parity_results.csv") != sha256(results_csv_path):
        errors.append("manifest hash mismatch for stage8c_parity_results.csv")

# 6. Data-license boundary: block private filenames and exact private artifact hashes anywhere in repo.
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    rel = path.relative_to(ROOT).as_posix()
    name = path.name.lower()
    if name == "efl_stage8_crsp_raw.csv" or (name.startswith("efl_stage8_") and name.endswith("_input.csv")):
        errors.append(f"private Stage VIII data filename must not be committed: {rel}")
        continue
    if rel.startswith("validation/real_data/private/"):
        errors.append(f"private Stage VIII directory content must not be committed: {rel}")
        continue
    # Hash files to catch renamed copies of the exact authorized private artifacts.
    try:
        digest = sha256(path)
    except OSError as exc:
        errors.append(f"unable to hash repository file {rel}: {exc}")
        continue
    if digest in PRIVATE_ARTIFACT_HASHES:
        errors.append(f"known private Stage VIII artifact committed under renamed path: {rel}")

if errors:
    print("STAGE VIII REAL-DATA EVIDENCE GATE: FAIL")
    for error in errors:
        print(" -", error)
    sys.exit(1)

print("STAGE VIII REAL-DATA EVIDENCE GATE: PASS (5 cases; public evidence only; no known private CRSP artifacts committed)")
