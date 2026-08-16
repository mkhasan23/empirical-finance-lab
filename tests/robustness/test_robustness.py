from __future__ import annotations

import json
from pathlib import Path

import pytest

from empirical_finance_lab.abnormal import compute_abnormal_returns
from empirical_finance_lab.audit import estimation_history_audit
from empirical_finance_lab.event_time import build_event_selection
from empirical_finance_lab.inference import classical_car_inference, permutation_inference
from empirical_finance_lab.robustness import run_robustness_matrix
from empirical_finance_lab.schema import AnalysisSpecification, PrimaryAnalysisResult
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes

ROOT = Path(__file__).resolve().parents[2]


def test_ROB001_two_model_prespecified_matrix():
    d = ROOT / "validation" / "robustness" / "ROB-001"
    spec = AnalysisSpecification.from_mapping(json.loads((d / "specification.json").read_text()))
    data = canonicalize_dataset(parse_csv_bytes((d / "data.csv").read_bytes()), spec)

    def analyze(variant):
        selection, audits = build_event_selection(data, variant)
        assert selection is not None
        abnormal = compute_abnormal_returns(data, variant, selection)
        classical = None
        if variant.model == "market_model":
            classical = classical_car_inference(abnormal.fit, data.benchmark_return[selection.event_indices], abnormal.car, direction=variant.inference.direction)
            K = 2
        else:
            K = 0
        perm = permutation_inference(abnormal.estimation_ar, abnormal.event_ar, K=K, B=variant.inference.permutation_B, seed=variant.inference.seed, direction=variant.inference.direction)
        return PrimaryAnalysisResult(selection, abnormal, classical, perm, (estimation_history_audit(len(abnormal.estimation_ar)),))

    rows = run_robustness_matrix(spec, analyze)
    expected = json.loads((d / "expected.json").read_text())["rows"]
    assert len(rows) == len(expected) == 2
    for got, exp in zip(rows, expected, strict=True):
        assert got["model"] == exp["model"]
        assert got["window"] == exp["window"]
        assert got["car"] == pytest.approx(exp["car"], abs=1e-12, rel=0)
        assert got["permutation_ge_count"] == exp["permutation_ge_count"]
        assert got["permutation_p_value"] == pytest.approx(exp["permutation_p_value"], abs=1e-12, rel=0)
        assert got["B"] == exp["B"]
        assert got["sign"] == exp["sign"]
        assert got["significant_5pct"] is exp["significant_5pct"]
