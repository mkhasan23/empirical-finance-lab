"""Classical and single-firm permutation inference."""
from __future__ import annotations

import itertools
import math
from typing import Iterable

import numpy as np
from scipy import stats

from .errors import EFLComputationError
from .schema import ClassicalInferenceResult, MarketModelFit, PermutationInferenceResult

PERM_COMPARISON_TOL = 1e-15


def classical_car_inference(
    fit: MarketModelFit,
    event_benchmark: np.ndarray,
    car: float,
    *,
    direction: str = "two_sided",
) -> ClassicalInferenceResult:
    event_benchmark = np.asarray(event_benchmark, dtype=np.float64)
    if not np.all(np.isfinite(event_benchmark)):
        raise EFLComputationError("NUM_NONFINITE", "Classical inference received nonfinite event benchmark returns.")
    m = len(event_benchmark)
    if m < 1:
        raise EFLComputationError("INF_INVALID_DF", "Event window must contain at least one observation.")
    x_sum = np.array([float(m), float(event_benchmark.sum())], dtype=np.float64)
    variance = float(fit.residual_variance * (m + x_sum @ fit.xtx_inv @ x_sum))
    if variance < 0.0 or not math.isfinite(variance):
        raise EFLComputationError("NUM_NONFINITE", "Classical CAR variance is invalid.")
    se = math.sqrt(variance)
    if se == 0.0:
        t_stat = 0.0 if car == 0.0 else math.copysign(math.inf, car)
    else:
        t_stat = float(car / se)
    if direction == "two_sided":
        p = 2.0 * float(stats.t.sf(abs(t_stat), fit.df))
    elif direction == "greater":
        p = float(stats.t.sf(t_stat, fit.df))
    elif direction == "less":
        p = float(stats.t.cdf(t_stat, fit.df))
    else:
        raise EFLComputationError("INF_DIRECTION_INVALID", f"Unsupported inference direction: {direction}")
    return ClassicalInferenceResult(
        method_id="EFL_CLASSICAL_PREDICTIVE_T_V1",
        car_variance=variance,
        car_se=se,
        t_statistic=t_stat,
        df=fit.df,
        p_value=p,
        direction=direction,
        assumptions=(
            "market-model disturbances are mean-zero conditional on the benchmark",
            "independent disturbances",
            "homoskedastic disturbances",
            "normal disturbances for finite-sample Student-t inference",
        ),
    )


def _raw_t_car(estimation_ar: np.ndarray, event_ar: np.ndarray, K: int) -> float:
    est = np.asarray(estimation_ar, dtype=np.float64)
    evt = np.asarray(event_ar, dtype=np.float64)
    n = len(est)
    m = len(evt)
    denom_df = n - K
    if denom_df <= 0:
        raise EFLComputationError("INF_INVALID_DF", "Permutation statistic has nonpositive estimation degrees of freedom.")
    if m <= 0:
        raise EFLComputationError("INF_INVALID_EVENT_WINDOW", "Permutation statistic requires at least one event observation.")
    s2 = float(est @ est) / denom_df
    car = float(evt.sum())
    if s2 <= 0.0:
        return 0.0 if car == 0.0 else math.copysign(math.inf, car)
    return float(car / math.sqrt(m * s2))


def permutation_test_statistic(estimation_ar: np.ndarray, event_ar: np.ndarray, K: int, direction: str) -> tuple[float, float]:
    raw = _raw_t_car(estimation_ar, event_ar, K)
    if direction == "two_sided":
        return raw, abs(raw)
    if direction in {"greater", "less"}:
        return raw, raw
    raise EFLComputationError("INF_DIRECTION_INVALID", f"Unsupported inference direction: {direction}")


def _is_extreme(candidate_raw: float, observed_raw: float, direction: str) -> bool:
    if direction == "two_sided":
        return abs(candidate_raw) >= abs(observed_raw) - PERM_COMPARISON_TOL
    if direction == "greater":
        return candidate_raw >= observed_raw - PERM_COMPARISON_TOL
    if direction == "less":
        return candidate_raw <= observed_raw + PERM_COMPARISON_TOL
    raise EFLComputationError("INF_DIRECTION_INVALID", f"Unsupported inference direction: {direction}")


def permutation_inference(
    estimation_ar: np.ndarray,
    event_ar: np.ndarray,
    *,
    K: int,
    B: int,
    seed: int,
    direction: str = "two_sided",
    record_first: int = 10,
) -> PermutationInferenceResult:
    est = np.asarray(estimation_ar, dtype=np.float64)
    evt = np.asarray(event_ar, dtype=np.float64)
    if not np.all(np.isfinite(est)) or not np.all(np.isfinite(evt)):
        raise EFLComputationError("NUM_NONFINITE", "Permutation inference received nonfinite abnormal returns.")
    if not 1_000 <= B <= 100_000:
        raise EFLComputationError("INF_PERMUTATION_COUNT_INVALID", "Permutation B must be between 1,000 and 100,000.")
    n, m = len(est), len(evt)
    values = np.concatenate((est, evt))
    N = n + m
    observed_raw, observed_stat = permutation_test_statistic(est, evt, K, direction)
    rng = np.random.Generator(np.random.PCG64(seed))
    ge_count = 1  # identity permutation is included first
    first: list[tuple[int, ...]] = [tuple(range(N))]
    for b in range(1, B):
        perm = rng.permutation(N)
        if b < record_first:
            first.append(tuple(int(x) for x in perm.tolist()))
        perm_est = values[perm[:n]]
        perm_evt = values[perm[n:]]
        candidate_raw = _raw_t_car(perm_est, perm_evt, K)
        if _is_extreme(candidate_raw, observed_raw, direction):
            ge_count += 1
    p = ge_count / B
    return PermutationInferenceResult(
        method_id="EFL_SINGLE_FIRM_PERMUTATION_V1",
        observed_t_car=observed_raw,
        observed_test_statistic=observed_stat,
        p_value=float(p),
        ge_count=int(ge_count),
        B=int(B),
        seed=int(seed),
        K=int(K),
        direction=direction,
        rng="PCG64",
        first_permutations=tuple(first),
    )


def exact_permutation_inference(
    estimation_ar: np.ndarray,
    event_ar: np.ndarray,
    *,
    K: int,
    direction: str = "two_sided",
) -> dict[str, float | int]:
    """Exhaustive reference helper for small validation fixtures; not used by normal runs."""
    est = np.asarray(estimation_ar, dtype=np.float64)
    evt = np.asarray(event_ar, dtype=np.float64)
    n, m = len(est), len(evt)
    values = np.concatenate((est, evt))
    observed_raw, observed_stat = permutation_test_statistic(est, evt, K, direction)
    ge = 0
    total = 0
    all_idx = tuple(range(n + m))
    for evt_idx in itertools.combinations(all_idx, m):
        evt_set = set(evt_idx)
        est_idx = [i for i in all_idx if i not in evt_set]
        candidate_raw = _raw_t_car(values[est_idx], values[list(evt_idx)], K)
        total += 1
        if _is_extreme(candidate_raw, observed_raw, direction):
            ge += 1
    return {
        "observed_t_car": observed_raw,
        "observed_test_statistic": observed_stat,
        "ge_count": ge,
        "assignment_count": total,
        "p_value": ge / total,
    }
