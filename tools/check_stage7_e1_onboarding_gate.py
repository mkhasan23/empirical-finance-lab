#!/usr/bin/env python3
"""Stage VII-E1 gate: deterministic synthetic onboarding and known-answer execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

from empirical_finance_lab.engine import run_analysis

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
CSV_PATH = EXAMPLES / "efl_tutorial_synthetic.csv"
SPEC_PATH = EXAMPLES / "efl_tutorial_specification.json"
GENERATOR_PATH = EXAMPLES / "generate_tutorial_dataset.py"
EXAMPLES_README = EXAMPLES / "README.md"
QUICKSTART = ROOT / "docs" / "quickstart.md"
EXPECTED_SHA256 = "e3b4d1004ee960106ac17618e680f5af4fb1c5286ff5d58234bb903bc321797e"
EXPECTED_AR = (0.01, 0.03, -0.01)
EXPECTED_CAR = 0.03
ABS_TOL = 1e-12
REL_TOL = 1e-10

errors: list[str] = []

for path in (CSV_PATH, SPEC_PATH, GENERATOR_PATH, EXAMPLES_README, QUICKSTART):
    if not path.is_file():
        errors.append(f"required Stage VII-E1 onboarding file is missing: {path.relative_to(ROOT)}")

if not errors:
    module_spec = importlib.util.spec_from_file_location("efl_tutorial_generator", GENERATOR_PATH)
    if module_spec is None or module_spec.loader is None:
        errors.append("could not load deterministic tutorial generator")
    else:
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        generated = module.build_csv_text().encode("utf-8")
        committed = CSV_PATH.read_bytes()
        if generated != committed:
            errors.append("committed tutorial CSV is not byte-identical to its deterministic generator")
        digest = hashlib.sha256(committed).hexdigest()
        if digest != EXPECTED_SHA256:
            errors.append(f"tutorial CSV SHA-256 drift: expected={EXPECTED_SHA256} actual={digest}")

expected_spec: dict[str, Any] = {
    "calendar_event_date": "2025-07-31",
    "effective_event_date": "2025-07-31",
    "estimation_window": {"end": -20, "start": -140},
    "event_timing": "during_or_before_market",
    "event_window": {"end": 1, "start": -1},
    "excluded_dates": [],
    "inference": {"direction": "two_sided", "permutation_B": 1000, "seed": 20260817},
    "locked": True,
    "model": "market_model",
    "placebo": {"enabled": False},
    "return_units": "decimal",
    "robustness_windows": [],
    "schema_version": "0.1.0",
}

specification: dict[str, Any] | None = None
if SPEC_PATH.is_file():
    try:
        specification = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"tutorial specification is not valid JSON: {exc}")
    else:
        if specification != expected_spec:
            errors.append("tutorial specification drifted from the Stage VII-E1 onboarding contract")

if CSV_PATH.is_file() and specification == expected_spec:
    outcome = run_analysis(CSV_PATH.read_bytes(), specification)
    if outcome.state != "COMPLETE" or outcome.primary is None:
        audit_codes = [audit.rule_id for audit in outcome.audits]
        errors.append(f"frozen Python core did not complete tutorial analysis: state={outcome.state}, audits={audit_codes}")
    else:
        abnormal = outcome.primary.abnormal
        event_ar = tuple(float(x) for x in abnormal.event_ar.tolist())
        if len(event_ar) != 3:
            errors.append(f"tutorial event AR length drift: expected=3 actual={len(event_ar)}")
        else:
            for tau, actual, expected in zip((-1, 0, 1), event_ar, EXPECTED_AR):
                if not math.isclose(actual, expected, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                    errors.append(f"tutorial AR({tau}) drift: expected={expected!r} actual={actual!r}")
        if not math.isclose(float(abnormal.car), EXPECTED_CAR, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            errors.append(f"tutorial CAR[-1,+1] drift: expected={EXPECTED_CAR!r} actual={float(abnormal.car)!r}")
        if abnormal.fit is None:
            errors.append("tutorial market-model fit is unexpectedly missing")
        else:
            if not math.isclose(float(abnormal.fit.alpha), 0.0004, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                errors.append(f"tutorial alpha drift: expected=0.0004 actual={float(abnormal.fit.alpha)!r}")
            if not math.isclose(float(abnormal.fit.beta), 1.15, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                errors.append(f"tutorial beta drift: expected=1.15 actual={float(abnormal.fit.beta)!r}")
        if len(outcome.primary.selection.estimation_indices) != 121:
            errors.append("tutorial estimation-window observation count drifted from 121")
        taus = tuple(int(x) for x in outcome.primary.selection.event_taus.tolist())
        if taus != (-1, 0, 1):
            errors.append(f"tutorial event-time selection drift: expected=(-1,0,1) actual={taus}")

if EXAMPLES_README.is_file():
    examples_text = EXAMPLES_README.read_text(encoding="utf-8")
    for required in (EXPECTED_SHA256, "fully synthetic", "CAR[-1,+1] = **+3.000%**", "frozen Python core"):
        if required not in examples_text:
            errors.append(f"examples/README.md onboarding invariant missing: {required}")

if QUICKSTART.is_file():
    quickstart_text = QUICKSTART.read_text(encoding="utf-8")
    for required in (
        "2025-07-31",
        "`-140`",
        "`-20`",
        "`1000`",
        "`20260817`",
        "CAR[-1,+1]: **+3.000%**",
        EXPECTED_SHA256,
        "Reproduce & cite",
    ):
        if required not in quickstart_text:
            errors.append(f"docs/quickstart.md onboarding invariant missing: {required}")

if errors:
    print("STAGE VII-E1 ONBOARDING GATE: FAIL")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)

print("STAGE VII-E1 ONBOARDING GATE: PASS")
print(" - deterministic synthetic CSV: PASS")
print(f" - tutorial CSV SHA-256: {EXPECTED_SHA256}")
print(" - frozen Python core: COMPLETE")
print(" - AR(-1), AR(0), AR(+1): +1.000%, +3.000%, -1.000%")
print(" - CAR[-1,+1]: +3.000%")
print(" - onboarding documentation contract: PASS")
