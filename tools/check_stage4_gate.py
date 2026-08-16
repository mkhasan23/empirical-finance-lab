#!/usr/bin/env python3
"""Stage IV static/runtime-risk gate. Pytest remains the numerical golden-output gate."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "empirical_finance_lab"
errors: list[str] = []

required_modules = {
    "abnormal.py", "audit.py", "diagnostics.py", "engine.py", "errors.py",
    "event_time.py", "inference.py", "models.py", "placebo.py", "reporting.py",
    "robustness.py", "runtime.py", "schema.py", "validation.py",
}
seen = {p.name for p in SRC.glob("*.py")}
missing = required_modules - seen
if missing:
    errors.append(f"missing Stage IV modules: {sorted(missing)}")

# Dependency boundary: the production scientific core is stdlib + NumPy + SciPy only.
for path in SRC.glob("*.py"):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "").split(".")[0]]
        else:
            continue
        for name in names:
            if name in {"pandas", "statsmodels", "sklearn"}:
                errors.append(f"forbidden production dependency {name} in {path.relative_to(ROOT)}")

# RNG boundary: no global seeding/default RNG in production scientific core.
joined = "\n".join(p.read_text(encoding="utf-8") for p in SRC.glob("*.py"))
for forbidden in ["np.random.seed(", "np.random.default_rng(", "numpy.random.seed(", "numpy.random.default_rng("]:
    if forbidden in joined:
        errors.append(f"forbidden implicit/global RNG construct found: {forbidden}")
if "np.random.PCG64(" not in joined:
    errors.append("explicit PCG64 construction not found")

# Stage III corpus must still pass untouched.
proc = subprocess.run([sys.executable, "tools/check_corpus_integrity.py"], cwd=ROOT, text=True, capture_output=True)
if proc.returncode != 0:
    errors.append("Stage III corpus integrity failed during Stage IV gate")

# Reference numerical environment for the Stage IV gate package.
expected_env = {"numpy": "2.3.5", "scipy": "1.17.0"}
actual_env = {"numpy": np.__version__, "scipy": scipy.__version__}
if actual_env != expected_env:
    errors.append(f"reference environment mismatch: expected={expected_env}, actual={actual_env}")

if errors:
    print("STAGE IV NUMERICAL CORE GATE: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("STAGE IV NUMERICAL CORE GATE: PASS")
print(f" - Stage III corpus: PASS")
print(f" - NumPy: {np.__version__}")
print(f" - SciPy: {scipy.__version__}")
print(f" - Production dependency boundary: PASS")
print(f" - Explicit PCG64 RNG boundary: PASS")
