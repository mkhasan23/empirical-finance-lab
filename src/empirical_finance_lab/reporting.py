"""Deterministic hashes, identifiers, and reproducibility manifests."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from typing import Any, Mapping

import numpy as np
import scipy

from . import __version__
from .schema import AnalysisSpecification, CanonicalDataset


def canonical_json_bytes(value: Any) -> bytes:
    """EFL v0.1 restricted canonical JSON serialization for hashing.

    Scientific specifications contain JSON strings, booleans, nulls, integers, arrays,
    and objects. Floating-point research data are *not* serialized through this function;
    canonical dataset hashing uses float.hex() below.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_dataset_bytes(dataset: CanonicalDataset) -> bytes:
    lines = ["EFL_CANONICAL_DATA_V1\n", "date\tsecurity_return_hex\tbenchmark_return_hex\n"]
    for d, s, b in zip(dataset.dates, dataset.security_return, dataset.benchmark_return, strict=True):
        sh = "MISSING" if np.isnan(s) else float(s).hex()
        bh = "MISSING" if np.isnan(b) else float(b).hex()
        lines.append(f"{d}\t{sh}\t{bh}\n")
    return "".join(lines).encode("utf-8")


def canonical_data_hash(dataset: CanonicalDataset) -> str:
    return sha256_hex(canonical_dataset_bytes(dataset))


def specification_hash(spec: AnalysisSpecification) -> str:
    return sha256_hex(canonical_json_bytes(spec.to_dict()))


def analysis_id(dataset: CanonicalDataset, spec: AnalysisSpecification) -> str:
    payload = (canonical_data_hash(dataset) + specification_hash(spec)).encode("ascii")
    return sha256_hex(payload)


def runtime_manifest(*, build_commit: str | None = None, pyodide_version: str | None = None, worker_protocol: str = "0.1.0") -> dict[str, Any]:
    return {
        "efl_version": __version__,
        "build_commit": build_commit or os.environ.get("EFL_BUILD_COMMIT", "UNSET"),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "pyodide": pyodide_version,
        "worker_protocol": worker_protocol,
        "platform": sys.platform,
    }


def rng_manifest(spec: AnalysisSpecification) -> dict[str, Any]:
    return {
        "algorithm": "PCG64",
        "seed": spec.inference.seed,
        "permutation_B": spec.inference.permutation_B,
        "algorithm_version": "EFL_SINGLE_FIRM_PERMUTATION_V1",
    }


def execution_id(
    analysis_id_value: str,
    *,
    runtime: Mapping[str, Any],
    rng: Mapping[str, Any],
) -> str:
    build_commit = str(runtime.get("build_commit", "UNSET"))
    payload = (
        analysis_id_value.encode("ascii")
        + __version__.encode("utf-8")
        + build_commit.encode("utf-8")
        + canonical_json_bytes(runtime)
        + canonical_json_bytes(rng)
    )
    return sha256_hex(payload)


def reproducibility_manifest(
    dataset: CanonicalDataset,
    spec: AnalysisSpecification,
    *,
    results: Mapping[str, Any] | None = None,
    build_commit: str | None = None,
) -> dict[str, Any]:
    c_hash = canonical_data_hash(dataset)
    s_hash = specification_hash(spec)
    a_id = sha256_hex((c_hash + s_hash).encode("ascii"))
    runtime = runtime_manifest(build_commit=build_commit)
    rng = rng_manifest(spec)
    e_id = execution_id(a_id, runtime=runtime, rng=rng)
    return {
        "software_version": __version__,
        "analysis_id": a_id,
        "execution_id": e_id,
        "hashes": {
            "raw_file_sha256": dataset.raw_file_hash,
            "canonical_data_sha256": c_hash,
            "specification_sha256": s_hash,
        },
        "analysis_specification": spec.to_dict(),
        "environment": runtime,
        "rng": rng,
        "results": dict(results or {}),
        "citation": {
            "software": "Empirical Finance Lab",
            "repository": "https://github.com/mkhasan23/empirical-finance-lab",
            "version": __version__,
        },
    }


def outcome_to_dict(outcome: "AnalysisOutcome") -> dict[str, Any]:
    """Serialize an AnalysisOutcome without recomputing any scientific quantity."""
    from .schema import AnalysisOutcome  # local import avoids a reporting/schema cycle at import time

    result: dict[str, Any] = {
        "state": outcome.state,
        "audits": [a.to_dict() for a in outcome.audits],
        "specification": outcome.specification.to_dict() if outcome.specification else None,
        "referee_report": outcome.referee_report,
        "reproducibility": dict(outcome.reproducibility) if outcome.reproducibility else None,
        "robustness": [dict(r) for r in outcome.robustness_rows],
    }
    if outcome.primary is not None and outcome.dataset is not None:
        p = outcome.primary
        a = p.abnormal
        event_rows = []
        for pos, idx in enumerate(a.event_indices):
            i = int(idx)
            event_rows.append({
                "date": outcome.dataset.dates[i],
                "tau": int(a.event_taus[pos]),
                "security_return": float(outcome.dataset.security_return[i]),
                "benchmark_return": float(outcome.dataset.benchmark_return[i]),
                "expected_return": float(a.event_expected[pos]),
                "abnormal_return": float(a.event_ar[pos]),
                "cumulative_abnormal_return": float(a.event_car_path[pos]),
            })
        model: dict[str, Any] = {"model": a.model, "usable_estimation_n": int(len(a.estimation_ar))}
        if a.fit is not None:
            model.update({
                "alpha": a.fit.alpha,
                "beta": a.fit.beta,
                "residual_variance": a.fit.residual_variance,
                "residual_scale": a.fit.residual_scale,
                "r_squared": a.fit.r_squared,
                "df": a.fit.df,
            })
        classical = None
        if p.classical is not None:
            classical = {
                "method_id": p.classical.method_id,
                "car_variance": p.classical.car_variance,
                "car_se": p.classical.car_se,
                "t_statistic": p.classical.t_statistic,
                "df": p.classical.df,
                "p_value": p.classical.p_value,
                "direction": p.classical.direction,
                "assumptions": list(p.classical.assumptions),
            }
        permutation = {
            "method_id": p.permutation.method_id,
            "observed_t_car": p.permutation.observed_t_car,
            "observed_test_statistic": p.permutation.observed_test_statistic,
            "p_value": p.permutation.p_value,
            "extreme_count": p.permutation.ge_count,
            "B": p.permutation.B,
            "seed": p.permutation.seed,
            "K": p.permutation.K,
            "direction": p.permutation.direction,
            "rng": p.permutation.rng,
        }
        result["primary"] = {
            "model": model,
            "car": a.car,
            "event_time": event_rows,
            "classical_inference": classical,
            "permutation_inference": permutation,
        }
    else:
        result["primary"] = None
    if outcome.placebo is not None:
        result["placebo"] = {
            "actual_car": outcome.placebo.actual_car,
            "candidate_count": outcome.placebo.P,
            "candidate_indices": list(outcome.placebo.candidate_indices),
            "candidate_dates": list(outcome.placebo.candidate_dates),
            "placebo_cars": list(outcome.placebo.placebo_cars),
            "extreme_count": outcome.placebo.extreme_count,
            "historical_placebo_tail_proportion": outcome.placebo.tail_proportion,
            "excluded_candidates": [dict(x) for x in outcome.placebo.excluded_candidates],
        }
    else:
        result["placebo"] = None
    return result
