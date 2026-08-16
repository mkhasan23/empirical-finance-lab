from __future__ import annotations

import json
from pathlib import Path

import pytest

from empirical_finance_lab.engine import run_analysis

ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_KA003_complete_and_reproducible():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    raw = (d / "data.csv").read_bytes()
    spec = json.loads((d / "specification.json").read_text())
    expected = json.loads((d / "expected.json").read_text())["expected"]
    outcome = run_analysis(raw, spec)
    assert outcome.state == "COMPLETE"
    assert outcome.primary is not None
    assert outcome.primary.abnormal.car == pytest.approx(expected["car_m1_p1"], abs=1e-12, rel=1e-10)
    assert outcome.reproducibility is not None
    assert len(outcome.reproducibility["analysis_id"]) == 64
    assert len(outcome.reproducibility["execution_id"]) == 64
    assert "Causal interpretation:** NOT ESTABLISHED" in outcome.referee_report
