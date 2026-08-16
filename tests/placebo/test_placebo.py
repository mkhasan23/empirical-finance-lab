from __future__ import annotations

import json
from pathlib import Path

import pytest

from empirical_finance_lab.abnormal import compute_abnormal_returns
from empirical_finance_lab.event_time import build_event_selection
from empirical_finance_lab.placebo import historical_placebo
from empirical_finance_lab.schema import AnalysisSpecification
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes

ROOT = Path(__file__).resolve().parents[2]


def test_PLC001_hand_enumerable_placebo():
    d = ROOT / "validation" / "placebo" / "PLC-001"
    spec = AnalysisSpecification.from_mapping(json.loads((d / "specification.json").read_text()))
    data = canonicalize_dataset(parse_csv_bytes((d / "data.csv").read_bytes()), spec)
    selection, audits = build_event_selection(data, spec)
    assert selection is not None
    primary = compute_abnormal_returns(data, spec, selection)
    result = historical_placebo(data, spec, actual_car=primary.car)
    expected = json.loads((d / "expected.json").read_text())["expected"]
    assert result.actual_car == pytest.approx(expected["actual_car"], abs=1e-12, rel=0)
    assert list(result.candidate_indices) == expected["candidate_indices"]
    assert list(result.candidate_dates) == expected["candidate_dates"]
    assert list(result.placebo_cars) == pytest.approx(expected["placebo_cars"], abs=1e-12, rel=0)
    assert result.P == expected["P"]
    assert result.extreme_count == expected["extreme_count"]
    assert result.tail_proportion == pytest.approx(expected["historical_placebo_tail_proportion"], abs=1e-12, rel=0)
