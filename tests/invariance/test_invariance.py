from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest

from empirical_finance_lab.engine import run_analysis
from empirical_finance_lab.reporting import canonical_data_hash
from empirical_finance_lab.schema import AnalysisSpecification
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes

ROOT = Path(__file__).resolve().parents[2]


def _ka3():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    return (d / "data.csv").read_bytes(), json.loads((d / "specification.json").read_text())


def test_row_order_invariance_after_explicit_sort_approval():
    raw, spec_map = _ka3()
    spec = AnalysisSpecification.from_mapping(spec_map)
    original = canonicalize_dataset(parse_csv_bytes(raw), spec)
    lines = raw.decode().splitlines()
    header, body = lines[0], lines[1:]
    # Deliberately swap two adjacent input rows; canonicalization is allowed only with explicit approval.
    body[20], body[21] = body[21], body[20]
    altered = (header + "\n" + "\n".join(body) + "\n").encode()
    normalized = canonicalize_dataset(parse_csv_bytes(altered), spec, sort_approved=True)
    assert canonical_data_hash(original) == canonical_data_hash(normalized)


def test_unit_invariance_decimal_vs_percent_numerical_result():
    raw, spec_dec = _ka3()
    out_dec = run_analysis(raw, spec_dec)
    rows = list(csv.DictReader(io.StringIO(raw.decode())))
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=["date", "security_return", "benchmark_return"], lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "date": row["date"],
            "security_return": str(float(row["security_return"]) * 100.0),
            "benchmark_return": str(float(row["benchmark_return"]) * 100.0),
        })
    spec_pct = dict(spec_dec)
    spec_pct["return_units"] = "percent"
    out_pct = run_analysis(buf.getvalue().encode(), spec_pct)
    assert out_dec.state == out_pct.state == "COMPLETE"
    assert out_dec.primary.abnormal.car == pytest.approx(out_pct.primary.abnormal.car, abs=1e-12, rel=1e-10)
    assert out_dec.primary.permutation.p_value == out_pct.primary.permutation.p_value


def test_unused_metadata_does_not_change_numerical_results():
    raw, spec_a = _ka3()
    spec_b = dict(spec_a)
    spec_b["display_label"] = "arbitrary non-analytical label"
    a = run_analysis(raw, spec_a)
    b = run_analysis(raw, spec_b)
    assert a.primary.abnormal.car == b.primary.abnormal.car
    assert a.primary.permutation.p_value == b.primary.permutation.p_value


def test_robustness_isolation_preserves_primary_result():
    raw, spec_base = _ka3()
    spec_rob = dict(spec_base)
    spec_rob["robustness_models"] = ["market_adjusted"]
    spec_rob["robustness_windows"] = [{"start": 0, "end": 0}]
    base = run_analysis(raw, spec_base)
    rob = run_analysis(raw, spec_rob)
    assert base.primary.abnormal.car == rob.primary.abnormal.car
    assert base.primary.permutation.ge_count == rob.primary.permutation.ge_count
    assert base.primary.permutation.p_value == rob.primary.permutation.p_value


def test_placebo_enablement_does_not_change_primary_permutation_stream():
    raw, spec_base = _ka3()
    spec_plc = dict(spec_base)
    spec_plc["placebo"] = {"enabled": True}
    base = run_analysis(raw, spec_base)
    plc = run_analysis(raw, spec_plc)
    assert base.primary.permutation.ge_count == plc.primary.permutation.ge_count
    assert base.primary.permutation.p_value == plc.primary.permutation.p_value
