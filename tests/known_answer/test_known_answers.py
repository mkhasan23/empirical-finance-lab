from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from empirical_finance_lab.abnormal import compute_abnormal_returns
from empirical_finance_lab.event_time import build_event_selection
from empirical_finance_lab.schema import AnalysisSpecification
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes, validate_parsed_dataset, validate_specification

ROOT = Path(__file__).resolve().parents[2]


def _case(fid: str):
    d = ROOT / "validation" / "known_answer" / fid
    raw = (d / "data.csv").read_bytes()
    spec_map = json.loads((d / "specification.json").read_text())
    expected = json.loads((d / "expected.json").read_text())
    spec = AnalysisSpecification.from_mapping(spec_map)
    parsed = parse_csv_bytes(raw)
    assert not any(a.evidence.get("blocks_calculation") for a in validate_specification(spec) + validate_parsed_dataset(parsed, spec))
    data = canonicalize_dataset(parsed, spec)
    selection, audits = build_event_selection(data, spec)
    assert selection is not None
    assert not any(a.evidence.get("blocks_calculation") for a in audits)
    result = compute_abnormal_returns(data, spec, selection)
    return result, expected


def test_KA001_zero_abnormal_returns():
    r, e = _case("KA-001")
    x = e["expected"]
    assert r.fit is not None
    assert r.fit.alpha == pytest.approx(x["alpha"], abs=1e-12, rel=1e-10)
    assert r.fit.beta == pytest.approx(x["beta"], abs=1e-12, rel=1e-10)
    np.testing.assert_allclose(r.event_ar, x["event_ar"], atol=1e-12, rtol=1e-10)
    assert r.car == pytest.approx(x["car"], abs=1e-12, rel=1e-10)


def test_KA002_known_five_percent_shock():
    r, e = _case("KA-002")
    x = e["expected"]
    assert r.fit is not None
    assert r.fit.alpha == pytest.approx(x["alpha"], abs=1e-12, rel=1e-10)
    assert r.fit.beta == pytest.approx(x["beta"], abs=1e-12, rel=1e-10)
    np.testing.assert_allclose(r.event_ar, x["event_ar"], atol=1e-12, rtol=1e-10)
    assert r.event_ar[1] == pytest.approx(x["ar_t0"], abs=1e-12, rel=1e-10)
    assert r.car == pytest.approx(x["car"], abs=1e-12, rel=1e-10)


def test_KA003_multiday_car():
    r, e = _case("KA-003")
    x = e["expected"]
    for tau, expected_ar in x["event_ar_by_tau"].items():
        pos = list(r.event_taus).index(int(tau))
        assert r.event_ar[pos] == pytest.approx(expected_ar, abs=1e-12, rel=1e-10)
    assert r.car == pytest.approx(x["car_m1_p1"], abs=1e-12, rel=1e-10)


def test_KA004_known_market_model_coefficients():
    r, e = _case("KA-004")
    x = e["expected"]
    assert r.fit is not None
    assert r.fit.n == x["estimation_n"]
    assert r.fit.alpha == pytest.approx(x["alpha_estimate"], abs=1e-12, rel=1e-10)
    assert r.fit.beta == pytest.approx(x["beta_estimate"], abs=1e-12, rel=1e-10)


def test_KA005_market_adjusted_definition():
    r, e = _case("KA-005")
    x = e["expected"]
    assert r.fit is None
    np.testing.assert_allclose(r.event_ar, x["event_ar"], atol=1e-12, rtol=1e-10)
    assert r.car == pytest.approx(x["car"], abs=1e-12, rel=1e-10)
