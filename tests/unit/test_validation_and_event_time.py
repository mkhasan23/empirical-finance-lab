from __future__ import annotations

import json
from pathlib import Path

from empirical_finance_lab.event_time import build_event_selection
from empirical_finance_lab.schema import AnalysisSpecification
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes, validate_parsed_dataset

ROOT = Path(__file__).resolve().parents[2]


def test_no_silent_sort_FM002():
    d = ROOT / "validation" / "failure_modes" / "FM-002"
    spec = AnalysisSpecification.from_mapping(json.loads((d / "specification.json").read_text()))
    parsed = parse_csv_bytes((d / "data.csv").read_bytes())
    audits = validate_parsed_dataset(parsed, spec)
    rule = next(a for a in audits if a.rule_id == "DATA_UNSORTED")
    assert rule.evidence["silent_sort_forbidden"] is True


def test_event_taus_are_trading_index_relative_not_calendar_day_relative():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    spec = AnalysisSpecification.from_mapping(json.loads((d / "specification.json").read_text()))
    data = canonicalize_dataset(parse_csv_bytes((d / "data.csv").read_bytes()), spec)
    selection, audits = build_event_selection(data, spec)
    assert selection is not None
    assert selection.event_taus.tolist() == [-1, 0, 1]
    assert data.dates[selection.event_index] == spec.effective_event_date
