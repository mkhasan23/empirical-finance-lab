from __future__ import annotations

import json
from pathlib import Path

import pytest

from empirical_finance_lab.engine import run_analysis
from empirical_finance_lab.reporting import specification_hash
from empirical_finance_lab.runtime import execution_acceptance, watchdog_decision
from empirical_finance_lab.schema import AnalysisSpecification

ROOT = Path(__file__).resolve().parents[2]
FM = ROOT / "validation" / "failure_modes"


def _load(fid: str):
    d = FM / fid
    expected = json.loads((d / "expected.json").read_text())["expected"]
    raw = (d / "data.csv").read_bytes() if (d / "data.csv").exists() else None
    spec = json.loads((d / "specification.json").read_text()) if (d / "specification.json").exists() else None
    scenario = json.loads((d / "scenario.json").read_text()) if (d / "scenario.json").exists() else None
    return raw, spec, expected, scenario


def _rule(outcome, rule_id):
    return next((a for a in outcome.audits if a.rule_id == rule_id), None)


@pytest.mark.parametrize("fid", ["FM-001", "FM-002", "FM-003", "FM-004", "FM-005", "FM-007", "FM-008", "FM-009", "FM-011"])
def test_blocking_failure_rules(fid):
    raw, spec, expected, _ = _load(fid)
    outcome = run_analysis(raw, spec)
    rule = _rule(outcome, expected["rule_id"])
    assert rule is not None, [a.to_dict() for a in outcome.audits]
    assert str(rule.status) == expected["status"]
    assert outcome.state == "BLOCKED"


def test_FM006_short_history_calculates_but_is_not_research_grade():
    raw, spec, expected, _ = _load("FM-006")
    outcome = run_analysis(raw, spec)
    rule = _rule(outcome, expected["rule_id"])
    assert outcome.state == "COMPLETE"
    assert rule is not None
    assert str(rule.status) == expected["status"]
    assert rule.evidence["usable_estimation_n"] == expected["usable_estimation_n"]
    assert rule.evidence["research_grade"] is expected["research_grade"]
    assert rule.evidence["calculation_may_run"] is expected["calculation_may_run"]


def test_FM010_extreme_return_preserved_warning_only():
    raw, spec, expected, _ = _load("FM-010")
    outcome = run_analysis(raw, spec)
    rule = _rule(outcome, expected["rule_id"])
    assert outcome.state == "COMPLETE"
    assert rule is not None
    assert str(rule.status) == expected["status"]
    assert rule.evidence["observation_preserved"] is True
    assert rule.evidence["automatic_winsorization"] is False


def test_FM012_no_placebo_candidate_does_not_destroy_primary_result():
    raw, spec, expected, _ = _load("FM-012")
    outcome = run_analysis(raw, spec)
    rule = _rule(outcome, expected["rule_id"])
    assert outcome.state == "COMPLETE"
    assert outcome.primary is not None
    assert outcome.placebo is not None and outcome.placebo.P == 0
    assert rule is not None
    assert str(rule.status) == expected["status"]
    assert rule.evidence["main_analysis_available"] is True


def test_FM013_changed_spec_changes_hash_and_analysis_identity_requirement():
    _, _, expected, scenario = _load("FM-013")
    a = AnalysisSpecification.from_mapping(scenario["initial_specification"])
    b = AnalysisSpecification.from_mapping(scenario["modified_specification"])
    assert specification_hash(a) != specification_hash(b)
    assert expected["new_spec_hash_required"] is True
    assert expected["new_analysis_id_required"] is True
    assert expected["prior_run_retained"] is True


def test_FM014_watchdog_timeout_contract():
    _, _, expected, scenario = _load("FM-014")
    got = watchdog_decision(scenario["simulated_elapsed_seconds"], scenario["watchdog_seconds"])
    assert got == expected


def test_FM015_stale_execution_contract():
    _, _, expected, scenario = _load("FM-015")
    got = execution_acceptance(scenario["current_execution_id"], scenario["returned_execution_id"])
    assert got == expected
