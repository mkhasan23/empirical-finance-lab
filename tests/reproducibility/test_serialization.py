from __future__ import annotations

import json
from pathlib import Path

from empirical_finance_lab import outcome_to_dict, run_analysis

ROOT = Path(__file__).resolve().parents[2]


def test_outcome_serialization_is_json_safe_and_does_not_change_results():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    outcome = run_analysis((d / "data.csv").read_bytes(), json.loads((d / "specification.json").read_text()))
    payload = outcome_to_dict(outcome)
    text = json.dumps(payload, sort_keys=True, allow_nan=False)
    restored = json.loads(text)
    assert restored["state"] == "COMPLETE"
    assert restored["primary"]["car"] == outcome.primary.abnormal.car
    assert restored["primary"]["permutation_inference"]["p_value"] == outcome.primary.permutation.p_value
    assert restored["reproducibility"]["analysis_id"] == outcome.reproducibility["analysis_id"]
