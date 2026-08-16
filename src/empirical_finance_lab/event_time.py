"""Event-time indexing and window construction."""
from __future__ import annotations

import numpy as np

from .schema import AnalysisSpecification, AuditResult, AuditStatus, CanonicalDataset, EventSelection


def _audit(rule_id: str, status: AuditStatus, message: str, **evidence: object) -> AuditResult:
    return AuditResult(rule_id=rule_id, stage="event", status=status, message=message, evidence=evidence)


def build_event_selection(dataset: CanonicalDataset, spec: AnalysisSpecification) -> tuple[EventSelection | None, tuple[AuditResult, ...]]:
    audits: list[AuditResult] = []
    if spec.effective_event_date is None:
        audits.append(_audit(
            "EVENT_EFFECTIVE_DATE_CONFIRMATION_REQUIRED", AuditStatus.WARNING,
            "Effective event trading date has not been confirmed.", blocks_calculation=True,
            analysis_lock_blocked=True,
        ))
        return None, tuple(audits)
    if spec.estimation_window.start <= spec.event_window.end and spec.estimation_window.end >= spec.event_window.start:
        audits.append(_audit(
            "EVENT_ESTIMATION_OVERLAP", AuditStatus.CRITICAL,
            "Estimation and event windows overlap.", blocks_calculation=True,
        ))
        return None, tuple(audits)
    try:
        event_index = dataset.dates.index(spec.effective_event_date)
    except ValueError:
        audits.append(_audit(
            "EVENT_EFFECTIVE_DATE_NOT_IN_CALENDAR", AuditStatus.CRITICAL,
            "Confirmed effective event date is not present in the uploaded trading calendar.",
            blocks_calculation=True, effective_event_date=spec.effective_event_date,
        ))
        return None, tuple(audits)
    est_start = event_index + spec.estimation_window.start
    est_end = event_index + spec.estimation_window.end
    evt_start = event_index + spec.event_window.start
    evt_end = event_index + spec.event_window.end
    if est_start < 0 or est_end >= dataset.n_rows:
        audits.append(_audit(
            "EST_WINDOW_OUT_OF_RANGE", AuditStatus.CRITICAL,
            "The requested estimation window is not fully represented in the uploaded trading history.",
            blocks_calculation=True, requested=[spec.estimation_window.start, spec.estimation_window.end],
        ))
    if evt_start < 0 or evt_end >= dataset.n_rows:
        audits.append(_audit(
            "EVENT_WINDOW_OUT_OF_RANGE", AuditStatus.CRITICAL,
            "The requested event window is not fully represented in the uploaded trading history.",
            blocks_calculation=True, requested=[spec.event_window.start, spec.event_window.end],
        ))
    if any(a.evidence.get("blocks_calculation") for a in audits):
        return None, tuple(audits)
    estimation_indices = np.arange(est_start, est_end + 1, dtype=np.int64)
    event_indices = np.arange(evt_start, evt_end + 1, dtype=np.int64)
    event_taus = np.arange(spec.event_window.start, spec.event_window.end + 1, dtype=np.int64)
    sec_evt = dataset.security_return[event_indices]
    bench_evt = dataset.benchmark_return[event_indices]
    incomplete = np.flatnonzero(~(np.isfinite(sec_evt) & np.isfinite(bench_evt)))
    if len(incomplete):
        bad_indices = event_indices[incomplete]
        audits.append(_audit(
            "EVENT_WINDOW_INCOMPLETE", AuditStatus.CRITICAL,
            "At least one required security or benchmark return is missing in the event window; CAR is not complete.",
            blocks_calculation=True, car_complete=False,
            dates=[dataset.dates[int(i)] for i in bad_indices],
            source_rows=[dataset.source_rows[int(i)] for i in bad_indices],
        ))
        return None, tuple(audits)
    return EventSelection(
        event_index=event_index,
        estimation_indices=estimation_indices,
        event_indices=event_indices,
        event_taus=event_taus,
    ), tuple(audits)
