"""Historical pseudo-event placebo diagnostic."""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from .abnormal import compute_abnormal_returns
from .event_time import build_event_selection
from .errors import EFLComputationError
from .schema import AnalysisSpecification, CanonicalDataset, PlaceboResult


def _direction_extreme(placebo_car: float, actual_car: float, direction: str) -> bool:
    tol = 1e-15
    if direction == "two_sided":
        return abs(placebo_car) >= abs(actual_car) - tol
    if direction == "greater":
        return placebo_car >= actual_car - tol
    if direction == "less":
        return placebo_car <= actual_car + tol
    raise ValueError(f"Unsupported direction: {direction}")


def historical_placebo(
    dataset: CanonicalDataset,
    spec: AnalysisSpecification,
    *,
    actual_car: float,
) -> PlaceboResult:
    if spec.effective_event_date is None:
        return PlaceboResult((), (), (), (), actual_car, 0, None)
    actual_index = dataset.dates.index(spec.effective_event_date)
    actual_evt = set(range(actual_index + spec.event_window.start, actual_index + spec.event_window.end + 1))
    excluded_dates = set(spec.excluded_dates)
    candidates: list[int] = []
    candidate_dates: list[str] = []
    cars: list[float] = []
    excluded: list[dict[str, object]] = []

    # "Historical" is operationalized as strictly pre-event candidate event dates.
    for candidate_index in range(actual_index):
        candidate_date = dataset.dates[candidate_index]
        est_start = candidate_index + spec.estimation_window.start
        est_end = candidate_index + spec.estimation_window.end
        evt_start = candidate_index + spec.event_window.start
        evt_end = candidate_index + spec.event_window.end
        reason = None
        if est_start < 0 or est_end >= dataset.n_rows or evt_start < 0 or evt_end >= dataset.n_rows:
            reason = "WINDOW_OUT_OF_RANGE"
        else:
            candidate_evt = set(range(evt_start, evt_end + 1))
            if candidate_evt & actual_evt:
                reason = "OVERLAPS_ACTUAL_EVENT_WINDOW"
            elif any(dataset.dates[i] in excluded_dates for i in candidate_evt):
                reason = "USER_EXCLUDED_DATE"
            elif not np.all(np.isfinite(dataset.security_return[evt_start:evt_end + 1]) & np.isfinite(dataset.benchmark_return[evt_start:evt_end + 1])):
                reason = "EVENT_WINDOW_INCOMPLETE"
        if reason is not None:
            excluded.append({"candidate_index": candidate_index, "candidate_date": candidate_date, "reason": reason})
            continue
        candidate_spec = replace(
            spec,
            calendar_event_date=candidate_date,
            effective_event_date=candidate_date,
            placebo_enabled=False,
            robustness_models=(),
            robustness_windows=(),
            locked=True,
        )
        selection, audits = build_event_selection(dataset, candidate_spec)
        if selection is None:
            excluded.append({"candidate_index": candidate_index, "candidate_date": candidate_date, "reason": "INVALID_CANDIDATE_SELECTION"})
            continue
        try:
            abnormal = compute_abnormal_returns(dataset, candidate_spec, selection)
        except (EFLComputationError, ValueError) as exc:
            excluded.append({"candidate_index": candidate_index, "candidate_date": candidate_date, "reason": getattr(exc, "code", "MODEL_FAILURE")})
            continue
        candidates.append(candidate_index)
        candidate_dates.append(candidate_date)
        cars.append(float(abnormal.car))
    P = len(candidates)
    if P == 0:
        return PlaceboResult((), (), (), tuple(excluded), actual_car, 0, None)
    extreme_count = sum(_direction_extreme(x, actual_car, spec.inference.direction) for x in cars)
    tail = (1 + extreme_count) / (P + 1)
    return PlaceboResult(
        candidate_indices=tuple(candidates),
        candidate_dates=tuple(candidate_dates),
        placebo_cars=tuple(cars),
        excluded_candidates=tuple(excluded),
        actual_car=float(actual_car),
        extreme_count=int(extreme_count),
        tail_proportion=float(tail),
    )
