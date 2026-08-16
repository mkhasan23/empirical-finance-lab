"""Prespecified robustness-matrix construction."""
from __future__ import annotations

from typing import Callable, Mapping

from .schema import AnalysisSpecification, PrimaryAnalysisResult


def robustness_variants(spec: AnalysisSpecification) -> tuple[AnalysisSpecification, ...]:
    variants = [spec.variant()]
    seen = {(spec.model, spec.event_window.start, spec.event_window.end)}
    for model in spec.robustness_models:
        key = (model, spec.event_window.start, spec.event_window.end)
        if key not in seen:
            variants.append(spec.variant(model=model))
            seen.add(key)
    for window in spec.robustness_windows:
        key = (spec.model, window.start, window.end)
        if key not in seen:
            variants.append(spec.variant(event_window=window))
            seen.add(key)
    return tuple(variants)


def run_robustness_matrix(
    spec: AnalysisSpecification,
    analyze_variant: Callable[[AnalysisSpecification], PrimaryAnalysisResult],
) -> tuple[Mapping[str, object], ...]:
    rows = []
    for variant in robustness_variants(spec):
        result = analyze_variant(variant)
        car = result.abnormal.car
        sign = "positive" if car > 0 else "negative" if car < 0 else "zero"
        rows.append({
            "model": variant.model,
            "window": [variant.event_window.start, variant.event_window.end],
            "car": float(car),
            "permutation_p_value": float(result.permutation.p_value),
            "permutation_ge_count": int(result.permutation.ge_count),
            "B": int(result.permutation.B),
            "sign": sign,
            "significant_5pct": bool(result.permutation.p_value < 0.05),
        })
    return tuple(rows)
