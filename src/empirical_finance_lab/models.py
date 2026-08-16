"""Expected-return model estimation."""
from __future__ import annotations

import math

import numpy as np

from .errors import EFLComputationError
from .schema import MarketModelFit


def fit_market_model(benchmark: np.ndarray, security: np.ndarray, used_indices: np.ndarray) -> MarketModelFit:
    benchmark = np.asarray(benchmark, dtype=np.float64)
    security = np.asarray(security, dtype=np.float64)
    used_indices = np.asarray(used_indices, dtype=np.int64)
    if not (len(benchmark) == len(security) == len(used_indices)):
        raise EFLComputationError("EST_DIMENSION_MISMATCH", "Market-model input arrays have inconsistent lengths.")
    if len(benchmark) < 3:
        raise EFLComputationError("EST_INVALID_DF", "Market model requires at least three usable estimation observations.")
    if not np.all(np.isfinite(benchmark)) or not np.all(np.isfinite(security)):
        raise EFLComputationError("NUM_NONFINITE", "Market-model estimation received nonfinite usable inputs.")
    n = len(benchmark)
    mbar = float(benchmark.mean())
    rbar = float(security.mean())
    centered_m = benchmark - mbar
    sxx = float(centered_m @ centered_m)
    if sxx == 0.0:
        raise EFLComputationError("EST_ZERO_BENCHMARK_VARIANCE", "Benchmark return has zero variance in the estimation window.")
    beta = float(centered_m @ (security - rbar) / sxx)
    alpha = float(rbar - beta * mbar)
    fitted = alpha + beta * benchmark
    residuals = security - fitted
    rss = float(residuals @ residuals)
    df = n - 2
    if df <= 0:
        raise EFLComputationError("EST_INVALID_DF", "Residual degrees of freedom are not positive.")
    residual_variance = rss / df
    if residual_variance < 0.0 or not math.isfinite(residual_variance):
        raise EFLComputationError("NUM_NONFINITE", "Residual variance is invalid.")
    residual_scale = math.sqrt(residual_variance)
    tss = float((security - rbar) @ (security - rbar))
    r_squared = 1.0 - rss / tss if tss > 0.0 else (1.0 if rss == 0.0 else 0.0)
    X = np.column_stack((np.ones(n, dtype=np.float64), benchmark))
    xtx = X.T @ X
    if np.linalg.matrix_rank(xtx) < 2:
        raise EFLComputationError("EST_RANK_DEFICIENT", "Market-model design matrix is rank deficient.")
    xtx_inv = np.linalg.inv(xtx)
    vals = [alpha, beta, residual_variance, residual_scale, rss, r_squared, mbar, sxx]
    if not all(math.isfinite(x) for x in vals):
        raise EFLComputationError("NUM_NONFINITE", "Market-model fit produced nonfinite quantities.")
    return MarketModelFit(
        alpha=alpha,
        beta=beta,
        residuals=residuals,
        fitted=fitted,
        residual_variance=residual_variance,
        residual_scale=residual_scale,
        rss=rss,
        r_squared=r_squared,
        n=n,
        df=df,
        benchmark_mean=mbar,
        sxx=sxx,
        xtx_inv=xtx_inv,
        used_indices=used_indices,
    )
