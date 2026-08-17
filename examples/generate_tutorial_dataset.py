#!/usr/bin/env python3
"""Generate the deterministic Stage VII-E1 synthetic onboarding dataset.

This dataset is entirely artificial. It is designed so the frozen EFL market-model
core recovers a known three-day abnormal-return path of +1%, +3%, -1%, giving a
CAR[-1,+1] of +3% under the documented tutorial specification.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import hashlib
import sys

START_DATE = date(2025, 1, 2)
END_DATE = date(2025, 9, 10)
EVENT_DATE = date(2025, 7, 31)
EXPECTED_ROWS = 180
EXPECTED_EVENT_INDEX = 150
EXPECTED_SHA256 = "e3b4d1004ee960106ac17618e680f5af4fb1c5286ff5d58234bb903bc321797e"


def _weekday_dates(start: date, end: date) -> list[date]:
    out: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            out.append(current)
        current += timedelta(days=1)
    return out


def build_csv_text() -> str:
    dates = _weekday_dates(START_DATE, END_DATE)
    if len(dates) != EXPECTED_ROWS:
        raise RuntimeError(f"tutorial date-grid drift: expected {EXPECTED_ROWS}, got {len(dates)}")
    event_index = dates.index(EVENT_DATE)
    if event_index != EXPECTED_EVENT_INDEX:
        raise RuntimeError(f"tutorial event-index drift: expected {EXPECTED_EVENT_INDEX}, got {event_index}")

    # For the documented estimation window [-140,-20], observations 10..130
    # form exactly eleven complete 11-observation cycles. The residual basis
    # below has zero mean and zero covariance with the benchmark basis over
    # each complete cycle, so OLS recovers alpha=0.0004 and beta=1.15.
    estimation_start_index = event_index - 140
    alpha = 0.0004
    beta = 1.15
    event_shocks = {-1: 0.01, 0: 0.03, 1: -0.01}

    lines = ["date,security_return,benchmark_return"]
    for index, trading_date in enumerate(dates):
        x = ((index - estimation_start_index) % 11) - 5
        benchmark = 0.0007 * x
        residual = 0.00012 * (x * x - 10)
        tau = index - event_index
        if tau in event_shocks:
            residual = event_shocks[tau]
        security = alpha + beta * benchmark + residual
        lines.append(f"{trading_date.isoformat()},{security:.12f},{benchmark:.12f}")
    return "\n".join(lines) + "\n"


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("efl_tutorial_synthetic.csv")
    payload = build_csv_text().encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"tutorial generator SHA-256 drift: expected {EXPECTED_SHA256}, got {digest}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    print(f"WROTE {output} ({EXPECTED_ROWS} rows, sha256={digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
