"""Typed scientific-core records for Empirical Finance Lab v0.1."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from copy import deepcopy
from enum import StrEnum
from typing import Any, Mapping, Sequence

import numpy as np


class AuditStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    NOT_ASSESSABLE = "NOT_ASSESSABLE"


@dataclass(frozen=True)
class AuditResult:
    rule_id: str
    stage: str
    status: AuditStatus
    message: str
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "stage": self.stage,
            "status": str(self.status),
            "message": self.message,
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True)
class Window:
    start: int
    end: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Window":
        return cls(start=int(value["start"]), end=int(value["end"]))

    def to_dict(self) -> dict[str, int]:
        return {"start": self.start, "end": self.end}

    @property
    def length(self) -> int:
        return self.end - self.start + 1


@dataclass(frozen=True)
class InferenceSpecification:
    direction: str = "two_sided"
    permutation_B: int = 20_000
    seed: int = 20260816

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "InferenceSpecification":
        value = value or {}
        return cls(
            direction=str(value.get("direction", "two_sided")),
            permutation_B=int(value.get("permutation_B", 20_000)),
            seed=int(value.get("seed", 20260816)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "direction": self.direction,
            "permutation_B": self.permutation_B,
            "seed": self.seed,
        }


@dataclass(frozen=True)
class AnalysisSpecification:
    schema_version: str
    return_units: str | None
    model: str
    calendar_event_date: str
    effective_event_date: str | None
    estimation_window: Window
    event_window: Window
    inference: InferenceSpecification
    locked: bool
    event_timing: str | None = None
    excluded_dates: tuple[str, ...] = ()
    robustness_windows: tuple[Window, ...] = ()
    robustness_models: tuple[str, ...] = ()
    placebo_enabled: bool = False
    source_mapping: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AnalysisSpecification":
        placebo = value.get("placebo") or {}
        return cls(
            schema_version=str(value.get("schema_version", "0.1.0")),
            return_units=value.get("return_units"),
            model=str(value.get("model", "market_model")),
            calendar_event_date=str(value.get("calendar_event_date", "")),
            effective_event_date=value.get("effective_event_date"),
            estimation_window=Window.from_mapping(value.get("estimation_window", {"start": -250, "end": -30})),
            event_window=Window.from_mapping(value.get("event_window", {"start": -1, "end": 1})),
            inference=InferenceSpecification.from_mapping(value.get("inference")),
            locked=bool(value.get("locked", False)),
            event_timing=value.get("event_timing"),
            excluded_dates=tuple(str(x) for x in value.get("excluded_dates", [])),
            robustness_windows=tuple(Window.from_mapping(x) for x in value.get("robustness_windows", [])),
            robustness_models=tuple(str(x) for x in value.get("robustness_models", [])),
            placebo_enabled=bool(placebo.get("enabled", False)),
            source_mapping=dict(value),
        )

    def to_dict(self) -> dict[str, Any]:
        # Preserve all caller-supplied specification fields so future material
        # metadata/normalization settings cannot silently disappear from SpecHash.
        out: dict[str, Any] = deepcopy(dict(self.source_mapping))
        out.update({
            "schema_version": self.schema_version,
            "model": self.model,
            "calendar_event_date": self.calendar_event_date,
            "effective_event_date": self.effective_event_date,
            "estimation_window": self.estimation_window.to_dict(),
            "event_window": self.event_window.to_dict(),
            "inference": self.inference.to_dict(),
            "locked": self.locked,
            "robustness_windows": [w.to_dict() for w in self.robustness_windows],
            "excluded_dates": list(self.excluded_dates),
            "placebo": {"enabled": self.placebo_enabled},
        })
        if self.return_units is None:
            out.pop("return_units", None)
        else:
            out["return_units"] = self.return_units
        if self.event_timing is None:
            out.pop("event_timing", None)
        else:
            out["event_timing"] = self.event_timing
        if self.robustness_models:
            out["robustness_models"] = list(self.robustness_models)
        else:
            out.pop("robustness_models", None)
        return out

    def variant(self, *, model: str | None = None, event_window: Window | None = None) -> "AnalysisSpecification":
        return replace(
            self,
            model=self.model if model is None else model,
            event_window=self.event_window if event_window is None else event_window,
            robustness_models=(),
            robustness_windows=(),
            placebo_enabled=False,
        )


@dataclass(frozen=True)
class ParsedRow:
    source_row: int
    date_text: str
    security_text: str
    benchmark_text: str


@dataclass(frozen=True)
class ParsedDataset:
    rows: tuple[ParsedRow, ...]
    raw_bytes: bytes


@dataclass(frozen=True)
class CanonicalDataset:
    dates: tuple[str, ...]
    security_return: np.ndarray
    benchmark_return: np.ndarray
    source_rows: tuple[int, ...]
    raw_file_hash: str

    def __post_init__(self) -> None:
        self.security_return.setflags(write=False)
        self.benchmark_return.setflags(write=False)
        if not (len(self.dates) == len(self.security_return) == len(self.benchmark_return) == len(self.source_rows)):
            raise ValueError("CanonicalDataset fields must have identical lengths")

    @property
    def n_rows(self) -> int:
        return len(self.dates)


@dataclass(frozen=True)
class EventSelection:
    event_index: int
    estimation_indices: np.ndarray
    event_indices: np.ndarray
    event_taus: np.ndarray

    def __post_init__(self) -> None:
        self.estimation_indices.setflags(write=False)
        self.event_indices.setflags(write=False)
        self.event_taus.setflags(write=False)


@dataclass(frozen=True)
class MarketModelFit:
    alpha: float
    beta: float
    residuals: np.ndarray
    fitted: np.ndarray
    residual_variance: float
    residual_scale: float
    rss: float
    r_squared: float
    n: int
    df: int
    benchmark_mean: float
    sxx: float
    xtx_inv: np.ndarray
    used_indices: np.ndarray

    def __post_init__(self) -> None:
        for arr in (self.residuals, self.fitted, self.xtx_inv, self.used_indices):
            arr.setflags(write=False)


@dataclass(frozen=True)
class AbnormalReturnResult:
    model: str
    estimation_ar: np.ndarray
    estimation_indices: np.ndarray
    event_expected: np.ndarray
    event_ar: np.ndarray
    event_car_path: np.ndarray
    car: float
    event_indices: np.ndarray
    event_taus: np.ndarray
    fit: MarketModelFit | None

    def __post_init__(self) -> None:
        for arr in (
            self.estimation_ar,
            self.estimation_indices,
            self.event_expected,
            self.event_ar,
            self.event_car_path,
            self.event_indices,
            self.event_taus,
        ):
            arr.setflags(write=False)


@dataclass(frozen=True)
class ClassicalInferenceResult:
    method_id: str
    car_variance: float
    car_se: float
    t_statistic: float
    df: int
    p_value: float
    direction: str
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class PermutationInferenceResult:
    method_id: str
    observed_t_car: float
    observed_test_statistic: float
    p_value: float
    ge_count: int
    B: int
    seed: int
    K: int
    direction: str
    rng: str
    first_permutations: tuple[tuple[int, ...], ...] = ()


@dataclass(frozen=True)
class PlaceboResult:
    candidate_indices: tuple[int, ...]
    candidate_dates: tuple[str, ...]
    placebo_cars: tuple[float, ...]
    excluded_candidates: tuple[Mapping[str, Any], ...]
    actual_car: float
    extreme_count: int
    tail_proportion: float | None

    @property
    def P(self) -> int:
        return len(self.candidate_indices)


@dataclass(frozen=True)
class PrimaryAnalysisResult:
    selection: EventSelection
    abnormal: AbnormalReturnResult
    classical: ClassicalInferenceResult | None
    permutation: PermutationInferenceResult
    audits: tuple[AuditResult, ...]


@dataclass(frozen=True)
class AnalysisOutcome:
    state: str
    audits: tuple[AuditResult, ...]
    dataset: CanonicalDataset | None = None
    specification: AnalysisSpecification | None = None
    primary: PrimaryAnalysisResult | None = None
    placebo: PlaceboResult | None = None
    robustness_rows: tuple[Mapping[str, Any], ...] = ()
    referee_report: str | None = None
    reproducibility: Mapping[str, Any] | None = None


def has_blocking_audit(audits: Sequence[AuditResult]) -> bool:
    return any(bool(a.evidence.get("blocks_calculation")) for a in audits)
