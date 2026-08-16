from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from empirical_finance_lab.abnormal import compute_abnormal_returns
from empirical_finance_lab.event_time import build_event_selection
from empirical_finance_lab.inference import classical_car_inference, exact_permutation_inference, permutation_inference
from empirical_finance_lab.schema import AnalysisSpecification
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes

ROOT = Path(__file__).resolve().parents[2]


def test_INF001_classical_predictive_car_inference():
    d = ROOT / "validation" / "inference" / "INF-001"
    spec = AnalysisSpecification.from_mapping(json.loads((d / "specification.json").read_text()))
    data = canonicalize_dataset(parse_csv_bytes((d / "data.csv").read_bytes()), spec)
    selection, audits = build_event_selection(data, spec)
    assert selection is not None
    abnormal = compute_abnormal_returns(data, spec, selection)
    assert abnormal.fit is not None
    result = classical_car_inference(abnormal.fit, data.benchmark_return[selection.event_indices], abnormal.car, direction="two_sided")
    expected = json.loads((d / "expected.json").read_text())["expected"]
    assert abnormal.fit.alpha == pytest.approx(expected["alpha"], abs=1e-12, rel=1e-10)
    assert abnormal.fit.beta == pytest.approx(expected["beta"], abs=1e-12, rel=1e-10)
    assert abnormal.fit.residual_variance == pytest.approx(expected["residual_variance"], abs=1e-12, rel=1e-10)
    assert result.df == expected["df"]
    assert abnormal.car == pytest.approx(expected["car"], abs=1e-12, rel=1e-10)
    assert result.car_variance == pytest.approx(expected["car_variance"], abs=1e-12, rel=1e-10)
    assert result.car_se == pytest.approx(expected["car_se"], abs=1e-12, rel=1e-10)
    assert result.t_statistic == pytest.approx(expected["t_statistic"], abs=1e-12, rel=1e-10)
    assert result.p_value == pytest.approx(expected["two_sided_p_value"], abs=1e-10, rel=0)


def _inf002_data():
    d = ROOT / "validation" / "inference" / "INF-002"
    rows = list(csv.DictReader((d / "data.csv").open()))
    est = np.array([float(r["abnormal_return"]) for r in rows if r["phase"] == "estimation"])
    evt = np.array([float(r["abnormal_return"]) for r in rows if r["phase"] == "event"])
    spec = json.loads((d / "specification.json").read_text())
    expected = json.loads((d / "expected.json").read_text())["expected"]
    return est, evt, spec, expected


def test_INF002_exact_enumeration():
    est, evt, spec, expected = _inf002_data()
    result = exact_permutation_inference(est, evt, K=spec["K"], direction=spec["direction"])
    assert abs(result["observed_test_statistic"] - expected["observed_abs_t_car"]) <= 1e-12
    assert result["assignment_count"] == expected["exact_assignment_count"]
    assert result["ge_count"] == expected["exact_ge_count"]
    assert result["p_value"] == pytest.approx(expected["exact_permutation_p_value"], abs=1e-12, rel=0)


def test_INF002_seeded_PCG64_permutation_reference():
    est, evt, spec, expected = _inf002_data()
    result = permutation_inference(est, evt, K=spec["K"], B=spec["B"], seed=spec["seed"], direction=spec["direction"], record_first=10)
    assert result.rng == "PCG64"
    assert result.observed_test_statistic == pytest.approx(expected["observed_abs_t_car"], abs=1e-12, rel=0)
    assert result.ge_count == expected["seeded_ge_count"]
    assert result.p_value == pytest.approx(expected["seeded_permutation_p_value"], abs=1e-12, rel=0)
    assert [list(x) for x in result.first_permutations] == expected["first_10_permutations"]
