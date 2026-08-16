"""Transparent model diagnostics used to audit inference assumptions."""
from __future__ import annotations

import math
from typing import Mapping

import numpy as np
from scipy import stats

from .schema import AuditResult, AuditStatus, MarketModelFit


def market_model_diagnostics(fit: MarketModelFit, event_ar: np.ndarray) -> tuple[Mapping[str, float | None], tuple[AuditResult, ...]]:
    """Return raw diagnostics and deterministic assumption warnings.

    Stage IV operationalization:
    - serial dependence: Ljung-Box Q(1), 5% warning threshold;
    - estimation-period variance instability: Brown-Forsythe/Levene median test
      comparing first and second halves, 5% warning threshold;
    - event scale is reported as mean squared event AR / estimation residual variance
      but is not treated as a formal event-induced-variance test in a single short event.
    """
    resid = np.asarray(fit.residuals, dtype=np.float64)
    evt = np.asarray(event_ar, dtype=np.float64)
    n = len(resid)
    diagnostics: dict[str, float | None] = {
        "lag1_autocorrelation": None,
        "ljung_box_q1": None,
        "ljung_box_q1_p_value": None,
        "brown_forsythe_p_value": None,
        "event_mean_square_to_estimation_variance": None,
    }
    audits: list[AuditResult] = []
    if n >= 3:
        x = resid[:-1]
        y = resid[1:]
        xdev = x - x.mean()
        ydev = y - y.mean()
        denom = math.sqrt(float(xdev @ xdev) * float(ydev @ ydev))
        rho1 = float((xdev @ ydev) / denom) if denom > 0.0 else 0.0
        q1 = float(n * (n + 2) * rho1 * rho1 / max(n - 1, 1))
        p_q1 = float(stats.chi2.sf(q1, 1))
        diagnostics.update(lag1_autocorrelation=rho1, ljung_box_q1=q1, ljung_box_q1_p_value=p_q1)
        if p_q1 < 0.05:
            audits.append(AuditResult(
                "INF_SERIAL_DEPENDENCE_WARNING", "inference", AuditStatus.WARNING,
                "Estimation residuals show statistically detectable lag-1 serial dependence under the Ljung-Box Q(1) diagnostic; permutation exchangeability and classical independence assumptions warrant caution.",
                {"p_value": p_q1, "lag1_autocorrelation": rho1, "blocks_calculation": False},
            ))
    if n >= 8:
        split = n // 2
        first = resid[:split]
        second = resid[split:]
        if np.ptp(resid) > 0.0:
            _, p_bf = stats.levene(first, second, center="median")
            p_bf = float(p_bf)
            diagnostics["brown_forsythe_p_value"] = p_bf
            if p_bf < 0.05:
                audits.append(AuditResult(
                    "INF_VARIANCE_WARNING", "inference", AuditStatus.WARNING,
                    "Estimation residual variance differs across the first and second halves under a Brown-Forsythe diagnostic; homoskedasticity/exchangeability assumptions warrant caution.",
                    {"p_value": p_bf, "blocks_calculation": False},
                ))
    if fit.residual_variance > 0.0 and len(evt):
        diagnostics["event_mean_square_to_estimation_variance"] = float(np.mean(evt * evt) / fit.residual_variance)
    return diagnostics, tuple(audits)
