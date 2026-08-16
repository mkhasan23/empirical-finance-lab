from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "validation"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_dir(category: str, fixture_id: str) -> Path:
    return VALIDATION / category / fixture_id


def load_case(category: str, fixture_id: str):
    d = fixture_dir(category, fixture_id)
    spec = load_json(d / "specification.json") if (d / "specification.json").exists() else None
    expected = load_json(d / "expected.json")
    raw = (d / "data.csv").read_bytes() if (d / "data.csv").exists() else None
    scenario = load_json(d / "scenario.json") if (d / "scenario.json").exists() else None
    return raw, spec, expected, scenario


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT
