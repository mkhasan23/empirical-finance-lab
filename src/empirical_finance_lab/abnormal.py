"""Expected returns, abnormal returns, and cumulative abnormal returns."""
from __future__ import annotations

import numpy as np

from .models import fit_market_model
from .schema import AbnormalReturnResult, AnalysisSpecification, CanonicalDataset, EventSelection


def compute_abnormal_returns(
    dataset: CanonicalDataset,
    spec: AnalysisSpecification,
    selection: EventSelection,
) -> AbnormalReturnResult:
    est_idx_all = selection.estimation_indices
    sec_est_all = dataset.security_return[est_idx_all]
    bench_est_all = dataset.benchmark_return[est_idx_all]
    usable = np.isfinite(sec_est_all) & np.isfinite(bench_est_all)
    est_idx = est_idx_all[usable]
    sec_est = sec_est_all[usable]
    bench_est = bench_est_all[usable]
    sec_evt = dataset.security_return[selection.event_indices]
    bench_evt = dataset.benchmark_return[selection.event_indices]
    if not np.all(np.isfinite(sec_evt) & np.isfinite(bench_evt)):
        raise ValueError("Event-window completeness must be validated before abnormal-return computation")
    if spec.model == "market_model":
        fit = fit_market_model(bench_est, sec_est, est_idx)
        estimation_ar = fit.residuals.copy()
        event_expected = fit.alpha + fit.beta * bench_evt
    elif spec.model == "market_adjusted":
        fit = None
        estimation_ar = sec_est - bench_est
        event_expected = bench_evt.copy()
    else:
        raise ValueError(f"Unsupported model: {spec.model}")
    event_ar = sec_evt - event_expected
    car_path = np.cumsum(event_ar, dtype=np.float64)
    car = float(car_path[-1]) if len(car_path) else 0.0
    return AbnormalReturnResult(
        model=spec.model,
        estimation_ar=np.asarray(estimation_ar, dtype=np.float64),
        estimation_indices=np.asarray(est_idx, dtype=np.int64),
        event_expected=np.asarray(event_expected, dtype=np.float64),
        event_ar=np.asarray(event_ar, dtype=np.float64),
        event_car_path=np.asarray(car_path, dtype=np.float64),
        car=car,
        event_indices=selection.event_indices.copy(),
        event_taus=selection.event_taus.copy(),
        fit=fit,
    )
