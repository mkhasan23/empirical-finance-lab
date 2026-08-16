"""Deterministic audit-rule helpers and Referee Mode templates."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping

from .schema import AuditResult, AuditStatus, PermutationInferenceResult, PlaceboResult


def estimation_history_audit(usable_n: int) -> AuditResult:
    if usable_n < 60:
        return AuditResult(
            "EST_SHORT_HISTORY", "estimation", AuditStatus.CRITICAL,
            "Fewer than 60 usable estimation observations are available; calculation may be exploratory but is not classified as research-grade.",
            {"usable_estimation_n": usable_n, "research_grade": False, "calculation_may_run": True, "blocks_calculation": False},
        )
    if usable_n < 120:
        return AuditResult(
            "EST_SHORT_HISTORY", "estimation", AuditStatus.WARNING,
            "The estimation history contains 60-119 usable observations; EFL flags this as a short-history warning.",
            {"usable_estimation_n": usable_n, "research_grade": True, "blocks_calculation": False},
        )
    return AuditResult(
        "EST_HISTORY_LENGTH", "estimation", AuditStatus.PASS,
        "At least 120 usable estimation observations are available.",
        {"usable_estimation_n": usable_n, "research_grade": True, "blocks_calculation": False},
    )


def model_failure_audit(code: str, message: str) -> AuditResult:
    rule = code if code.startswith("EST_") else "NUM_NONFINITE"
    return AuditResult(rule, "estimation", AuditStatus.CRITICAL, message, {"blocks_calculation": True})


def placebo_no_candidates_audit() -> AuditResult:
    return AuditResult(
        "PLC_NO_ADMISSIBLE_DATES", "placebo", AuditStatus.NOT_ASSESSABLE,
        "No admissible historical pseudo-event dates satisfy the locked placebo rules; the main analysis remains available.",
        {"blocks_calculation": False, "main_analysis_available": True},
    )


def confounder_not_assessable_audit() -> AuditResult:
    return AuditResult(
        "INT_CONFOUNDERS_NOT_ASSESSABLE", "interpretation", AuditStatus.NOT_ASSESSABLE,
        "External confounding announcements are not independently observable from the uploaded return file.",
        {"blocks_calculation": False},
    )


def causal_not_established_audit() -> AuditResult:
    return AuditResult(
        "INT_CAUSAL_NOT_ESTABLISHED", "interpretation", AuditStatus.WARNING,
        "A short-horizon event-study association does not by itself establish causal attribution.",
        {"blocks_calculation": False},
    )


def _stage_status(audits: Iterable[AuditResult], prefix: str | None = None, stage: str | None = None) -> str:
    relevant = [a for a in audits if (prefix is None or a.rule_id.startswith(prefix)) and (stage is None or a.stage == stage)]
    if not relevant:
        return "PASS"
    statuses = {a.status for a in relevant}
    if AuditStatus.CRITICAL in statuses:
        return "CRITICAL"
    if AuditStatus.WARNING in statuses:
        return "WARNING"
    if AuditStatus.NOT_ASSESSABLE in statuses:
        return "NOT ASSESSABLE"
    return "PASS"


def build_referee_report(
    audits: Iterable[AuditResult],
    permutation: PermutationInferenceResult | None,
    placebo: PlaceboResult | None,
) -> str:
    audits = tuple(audits)
    permutation_label = "NOT ASSESSABLE"
    if permutation is not None:
        assumption_warning = any(a.rule_id in {"INF_SERIAL_DEPENDENCE_WARNING", "INF_VARIANCE_WARNING"} for a in audits)
        permutation_label = "ASSUMPTION WARNING" if assumption_warning else ("SUPPORTIVE" if permutation.p_value < 0.05 else "NOT SUPPORTIVE")
    placebo_label = "NOT ASSESSABLE"
    if placebo is not None and placebo.tail_proportion is not None:
        placebo_label = "UNUSUAL" if placebo.tail_proportion <= 0.05 else "NOT UNUSUAL"
    lines = [
        "# Empirical Finance Lab — Referee Mode",
        "",
        f"**Computational validity:** {"CRITICAL" if any(a.evidence.get("blocks_calculation") for a in audits) else "PASS"}",
        f"**Data integrity:** {_stage_status(audits, prefix='DATA_')}",
        f"**Event-time integrity:** {_stage_status(audits, prefix='EVENT_')}",
        f"**Estimation integrity:** {_stage_status(audits, prefix='EST_')}",
        f"**Permutation inference:** {permutation_label}",
        f"**Historical placebo evidence:** {placebo_label}",
        f"**Confounding events:** {_stage_status(audits, prefix='INT_CONFOUNDERS_')}",
        "**Causal interpretation:** NOT ESTABLISHED",
        "",
        "The labels above are deterministic summaries of version-controlled audit rules. Statistical significance or an extreme placebo position does not by itself establish causality.",
    ]
    return "\n".join(lines) + "\n"
