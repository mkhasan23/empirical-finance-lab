from __future__ import annotations

import json
from pathlib import Path

from empirical_finance_lab.engine import run_analysis

ROOT = Path(__file__).resolve().parents[2]


def test_referee_mode_preserves_permutation_assumption_warning():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    outcome = run_analysis((d / "data.csv").read_bytes(), json.loads((d / "specification.json").read_text()))
    assert outcome.state == "COMPLETE"
    serial = next(a for a in outcome.audits if a.rule_id == "INF_SERIAL_DEPENDENCE_WARNING")
    assert serial.status == "WARNING"
    assert "Permutation inference:** ASSUMPTION WARNING" in outcome.referee_report
    assert "Computational validity:** PASS" in outcome.referee_report
