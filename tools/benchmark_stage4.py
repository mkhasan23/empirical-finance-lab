#!/usr/bin/env python3
"""Deterministic Stage IV engineering benchmark; no scientific acceptance thresholds are changed here."""
from __future__ import annotations

import csv
import io
import json
import statistics
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from empirical_finance_lab import run_analysis

ROOT = Path(__file__).resolve().parents[1]


def time_call(fn, repeats: int = 3):
    values = []
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn()
        values.append(time.perf_counter() - t0)
    return result, values


def primary_case():
    d = ROOT / "validation" / "known_answer" / "KA-003"
    raw = (d / "data.csv").read_bytes()
    spec = json.loads((d / "specification.json").read_text(encoding="utf-8"))
    return run_analysis(raw, spec)


def placebo_10k_case():
    start = date(1990, 1, 1)
    n = 10_000
    e = n - 2
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["date", "security_return", "benchmark_return"])
    for i in range(n):
        d = (start + timedelta(days=i)).isoformat()
        b = 0.001 * np.sin(i * 0.13)
        s = b + 0.002 * np.sin(i * 0.31)
        writer.writerow([d, s, b])
    event = (start + timedelta(days=e)).isoformat()
    spec = {
        "schema_version": "0.1.0",
        "return_units": "decimal",
        "model": "market_adjusted",
        "calendar_event_date": event,
        "effective_event_date": event,
        "event_timing": "during_or_before_market",
        "estimation_window": {"start": -250, "end": -30},
        "event_window": {"start": -1, "end": 1},
        "inference": {"direction": "two_sided", "permutation_B": 20_000, "seed": 20260816},
        "placebo": {"enabled": True},
        "excluded_dates": [],
        "robustness_windows": [],
        "locked": True,
    }
    return run_analysis(buf.getvalue().encode("utf-8"), spec)


if __name__ == "__main__":
    primary, t_primary = time_call(primary_case)
    placebo, t_placebo = time_call(placebo_10k_case)
    output = {
        "primary_20000_permutation_seconds": t_primary,
        "primary_20000_permutation_median_seconds": statistics.median(t_primary),
        "placebo_10000_rows_seconds": t_placebo,
        "placebo_10000_rows_median_seconds": statistics.median(t_placebo),
        "primary_state": primary.state,
        "placebo_state": placebo.state,
        "placebo_candidate_count": placebo.placebo.P if placebo.placebo is not None else None,
    }
    print(json.dumps(output, indent=2))
