from __future__ import annotations

import json
from pathlib import Path

from empirical_finance_lab.reporting import analysis_id, canonical_data_hash, reproducibility_manifest, specification_hash
from empirical_finance_lab.schema import AnalysisSpecification
from empirical_finance_lab.validation import canonicalize_dataset, parse_csv_bytes

ROOT = Path(__file__).resolve().parents[2]


def test_hashes_are_deterministic_and_spec_sensitive():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    raw = (d / "data.csv").read_bytes()
    spec_map = json.loads((d / "specification.json").read_text())
    spec = AnalysisSpecification.from_mapping(spec_map)
    data = canonicalize_dataset(parse_csv_bytes(raw), spec)
    c1 = canonical_data_hash(data)
    c2 = canonical_data_hash(data)
    s1 = specification_hash(spec)
    s2 = specification_hash(spec)
    a1 = analysis_id(data, spec)
    a2 = analysis_id(data, spec)
    assert c1 == c2
    assert s1 == s2
    assert a1 == a2
    modified = dict(spec_map)
    modified["event_window"] = {"start": -2, "end": 2}
    spec2 = AnalysisSpecification.from_mapping(modified)
    assert specification_hash(spec2) != s1
    assert analysis_id(data, spec2) != a1


def test_reproducibility_manifest_repeats_in_same_runtime():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    raw = (d / "data.csv").read_bytes()
    spec = AnalysisSpecification.from_mapping(json.loads((d / "specification.json").read_text()))
    data = canonicalize_dataset(parse_csv_bytes(raw), spec)
    m1 = reproducibility_manifest(data, spec, build_commit="TEST")
    m2 = reproducibility_manifest(data, spec, build_commit="TEST")
    assert m1["analysis_id"] == m2["analysis_id"]
    assert m1["execution_id"] == m2["execution_id"]
    assert m1["hashes"] == m2["hashes"]
