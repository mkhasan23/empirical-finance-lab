"""Authoritative Stage IV numerical-core orchestration."""
from __future__ import annotations

from typing import Mapping

import numpy as np

from .abnormal import compute_abnormal_returns
from .audit import (
    build_referee_report,
    causal_not_established_audit,
    confounder_not_assessable_audit,
    estimation_history_audit,
    model_failure_audit,
    placebo_no_candidates_audit,
)
from .errors import EFLComputationError, EFLValidationError
from .event_time import build_event_selection
from .diagnostics import market_model_diagnostics
from .inference import classical_car_inference, permutation_inference
from .placebo import historical_placebo
from .reporting import reproducibility_manifest
from .robustness import run_robustness_matrix
from .schema import (
    AnalysisOutcome,
    AnalysisSpecification,
    AuditResult,
    AuditStatus,
    CanonicalDataset,
    PrimaryAnalysisResult,
    has_blocking_audit,
)
from .validation import canonicalize_dataset, parse_csv_bytes, validate_parsed_dataset, validate_specification


def _primary_analysis(dataset: CanonicalDataset, spec: AnalysisSpecification) -> PrimaryAnalysisResult:
    selection, selection_audits = build_event_selection(dataset, spec)
    if selection is None:
        raise EFLValidationError("EVENT_SELECTION_BLOCKED", "Event-time selection is blocked.", {"audits": [a.to_dict() for a in selection_audits]})
    audits: list[AuditResult] = list(selection_audits)
    try:
        abnormal = compute_abnormal_returns(dataset, spec, selection)
    except EFLComputationError as exc:
        raise
    audits.append(estimation_history_audit(len(abnormal.estimation_ar)))
    requested_estimation_n = len(selection.estimation_indices)
    usable_estimation_n = len(abnormal.estimation_ar)
    dropped_estimation_n = requested_estimation_n - usable_estimation_n
    if dropped_estimation_n > 0:
        audits.append(AuditResult(
            "EST_MISSING_OBSERVATIONS", "estimation", AuditStatus.WARNING,
            "One or more requested estimation-window observations were excluded pairwise because a security or benchmark return was missing.",
            {
                "requested_estimation_n": requested_estimation_n,
                "usable_estimation_n": usable_estimation_n,
                "dropped_estimation_n": dropped_estimation_n,
                "missingness_fraction": dropped_estimation_n / requested_estimation_n,
                "blocks_calculation": False,
            },
        ))
    classical = None
    if spec.model == "market_model":
        assert abnormal.fit is not None
        classical = classical_car_inference(
            abnormal.fit,
            dataset.benchmark_return[selection.event_indices],
            abnormal.car,
            direction=spec.inference.direction,
        )
        _, diagnostic_audits = market_model_diagnostics(abnormal.fit, abnormal.event_ar)
        audits.extend(diagnostic_audits)
        K = 2
    else:
        K = 0
    permutation = permutation_inference(
        abnormal.estimation_ar,
        abnormal.event_ar,
        K=K,
        B=spec.inference.permutation_B,
        seed=spec.inference.seed,
        direction=spec.inference.direction,
    )
    return PrimaryAnalysisResult(
        selection=selection,
        abnormal=abnormal,
        classical=classical,
        permutation=permutation,
        audits=tuple(audits),
    )


def run_analysis(raw_csv: bytes, specification: Mapping[str, object]) -> AnalysisOutcome:
    spec = AnalysisSpecification.from_mapping(specification)
    parsed = parse_csv_bytes(raw_csv)
    audits: list[AuditResult] = list(validate_specification(spec))
    audits.extend(validate_parsed_dataset(parsed, spec))
    if has_blocking_audit(audits):
        return AnalysisOutcome(state="BLOCKED", audits=tuple(audits), specification=spec)
    try:
        dataset = canonicalize_dataset(parsed, spec)
    except EFLValidationError as exc:
        audits.append(AuditResult(exc.code, "input", AuditStatus.CRITICAL, str(exc), {"blocks_calculation": True}))
        return AnalysisOutcome(state="BLOCKED", audits=tuple(audits), specification=spec)
    selection, event_audits = build_event_selection(dataset, spec)
    audits.extend(event_audits)
    if selection is None or has_blocking_audit(audits):
        return AnalysisOutcome(state="BLOCKED", audits=tuple(audits), dataset=dataset, specification=spec)
    try:
        primary = _primary_analysis(dataset, spec)
    except EFLComputationError as exc:
        audits.append(model_failure_audit(exc.code, str(exc)))
        return AnalysisOutcome(state="BLOCKED", audits=tuple(audits), dataset=dataset, specification=spec)
    # Avoid duplicating event-selection audits already collected by the outer layer.
    audits.extend(a for a in primary.audits if a.rule_id not in {x.rule_id for x in audits})

    placebo = None
    if spec.placebo_enabled:
        placebo = historical_placebo(dataset, spec, actual_car=primary.abnormal.car)
        if placebo.P == 0:
            audits.append(placebo_no_candidates_audit())

    def analyze_variant(variant: AnalysisSpecification) -> PrimaryAnalysisResult:
        return _primary_analysis(dataset, variant)

    robustness_rows = ()
    if spec.robustness_models or spec.robustness_windows:
        robustness_rows = run_robustness_matrix(spec, analyze_variant)

    audits.append(confounder_not_assessable_audit())
    audits.append(causal_not_established_audit())
    referee = build_referee_report(audits, primary.permutation, placebo)
    result_summary = {
        "model": spec.model,
        "event_window": spec.event_window.to_dict(),
        "car": primary.abnormal.car,
        "permutation_p_value": primary.permutation.p_value,
        "classical_p_value": primary.classical.p_value if primary.classical else None,
    }
    repro = reproducibility_manifest(dataset, spec, results=result_summary)
    return AnalysisOutcome(
        state="COMPLETE",
        audits=tuple(audits),
        dataset=dataset,
        specification=spec,
        primary=primary,
        placebo=placebo,
        robustness_rows=tuple(robustness_rows),
        referee_report=referee,
        reproducibility=repro,
    )
