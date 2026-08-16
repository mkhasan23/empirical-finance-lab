"""CSV/specification validation and explicit canonicalization."""
from __future__ import annotations

import csv
import hashlib
import io
import math
from datetime import date
from typing import Iterable

import numpy as np

from .errors import EFLValidationError
from .schema import (
    AnalysisSpecification,
    AuditResult,
    AuditStatus,
    CanonicalDataset,
    ParsedDataset,
    ParsedRow,
)

MAX_ROWS = 25_000
EXTREME_POSITIVE_RETURN_THRESHOLD = 2.0  # non-destructive engineering warning only


def raw_file_hash(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def parse_csv_bytes(raw_bytes: bytes) -> ParsedDataset:
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise EFLValidationError("DATA_ENCODING", "CSV must be UTF-8 encoded.") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    required = {"date", "security_return", "benchmark_return"}
    if reader.fieldnames is None or not required.issubset(reader.fieldnames):
        raise EFLValidationError(
            "DATA_REQUIRED_COLUMNS",
            "CSV must contain date, security_return, and benchmark_return columns.",
            {"fieldnames": reader.fieldnames or []},
        )
    rows = []
    for source_row, row in enumerate(reader, start=2):
        rows.append(
            ParsedRow(
                source_row=source_row,
                date_text=(row.get("date") or "").strip(),
                security_text=(row.get("security_return") or "").strip(),
                benchmark_text=(row.get("benchmark_return") or "").strip(),
            )
        )
    return ParsedDataset(rows=tuple(rows), raw_bytes=raw_bytes)


def _audit(rule_id: str, stage: str, status: AuditStatus, message: str, **evidence: object) -> AuditResult:
    return AuditResult(rule_id=rule_id, stage=stage, status=status, message=message, evidence=evidence)


def _parse_return(text: str, units: str | None) -> float:
    if text == "":
        return math.nan
    try:
        value = float(text)
    except ValueError:
        return math.nan
    if not math.isfinite(value):
        return value
    if units == "percent":
        value /= 100.0
    return value


def validate_specification(spec: AnalysisSpecification) -> tuple[AuditResult, ...]:
    out: list[AuditResult] = []
    if spec.return_units not in {"decimal", "percent"}:
        out.append(_audit(
            "DATA_RETURN_UNITS_REQUIRED", "input", AuditStatus.CRITICAL,
            "Return units must be explicitly declared as decimal or percent before analysis can lock.",
            blocks_calculation=True, analysis_lock_blocked=True,
        ))
    if spec.model not in {"market_model", "market_adjusted"}:
        out.append(_audit(
            "ROB_SPEC_INVALID", "specification", AuditStatus.CRITICAL,
            "Unsupported expected-return model.", blocks_calculation=True, model=spec.model,
        ))
    if spec.estimation_window.start > spec.estimation_window.end:
        out.append(_audit(
            "EST_WINDOW_INVALID", "estimation", AuditStatus.CRITICAL,
            "Estimation-window start must not exceed its end.", blocks_calculation=True,
        ))
    if spec.event_window.start > spec.event_window.end:
        out.append(_audit(
            "EVENT_WINDOW_INVALID", "event", AuditStatus.CRITICAL,
            "Event-window start must not exceed its end.", blocks_calculation=True,
        ))
    if spec.event_window.length > 11:
        out.append(_audit(
            "EVENT_WINDOW_TOO_LONG", "event", AuditStatus.CRITICAL,
            "v0.1 supports short-horizon event windows of at most 11 trading days.",
            blocks_calculation=True, length=spec.event_window.length,
        ))
    if len(spec.robustness_windows) > 3:
        out.append(_audit(
            "ROB_SPEC_INVALID", "robustness", AuditStatus.CRITICAL,
            "v0.1 permits at most three prespecified robustness event windows.", blocks_calculation=True,
        ))
    invalid_robustness_models = [m for m in spec.robustness_models if m not in {"market_model", "market_adjusted"}]
    if invalid_robustness_models:
        out.append(_audit(
            "ROB_SPEC_INVALID", "robustness", AuditStatus.CRITICAL,
            "One or more prespecified robustness models are unsupported in v0.1.",
            blocks_calculation=True, models=invalid_robustness_models,
        ))
    for w in spec.robustness_windows:
        if w.start > w.end or w.length > 11:
            out.append(_audit(
                "ROB_SPEC_INVALID", "robustness", AuditStatus.CRITICAL,
                "Each robustness window must be ordered and contain at most 11 trading days.",
                blocks_calculation=True, window=w.to_dict(),
            ))
    if spec.inference.direction not in {"two_sided", "greater", "less"}:
        out.append(_audit(
            "INF_DIRECTION_INVALID", "inference", AuditStatus.CRITICAL,
            "Inference direction must be two_sided, greater, or less.", blocks_calculation=True,
        ))
    if not 1_000 <= spec.inference.permutation_B <= 100_000:
        out.append(_audit(
            "INF_PERMUTATION_COUNT_INVALID", "inference", AuditStatus.CRITICAL,
            "Permutation count must lie between 1,000 and 100,000 in v0.1.",
            blocks_calculation=True, B=spec.inference.permutation_B,
        ))
    if spec.inference.seed < 0:
        out.append(_audit(
            "INF_SEED_INVALID", "inference", AuditStatus.CRITICAL,
            "Random seed must be a nonnegative integer.", blocks_calculation=True,
        ))
    if spec.effective_event_date is None:
        out.append(_audit(
            "EVENT_EFFECTIVE_DATE_CONFIRMATION_REQUIRED", "event", AuditStatus.WARNING,
            "The effective event trading date must be explicitly confirmed; EFL does not silently shift calendar dates.",
            blocks_calculation=True, analysis_lock_blocked=True,
        ))
    elif spec.event_timing in {None, "unknown", "uncertain"}:
        out.append(_audit(
            "EVENT_ALIGNMENT_UNCERTAIN", "event", AuditStatus.WARNING,
            "The effective trading date is confirmed but announcement timing is uncertain; event-window interpretation should span the timing ambiguity where appropriate.",
            blocks_calculation=False,
        ))
    if not spec.locked:
        # A deliberately unlocked spec may be valid as a draft, but numerical execution is not allowed.
        out.append(_audit(
            "SPEC_NOT_LOCKED", "specification", AuditStatus.WARNING,
            "The analysis specification is not locked; numerical execution is unavailable until it is locked.",
            blocks_calculation=True, analysis_lock_blocked=True,
        ))
    # Estimation and event windows may not overlap in relative event time.
    if spec.estimation_window.start <= spec.event_window.end and spec.estimation_window.end >= spec.event_window.start:
        out.append(_audit(
            "EVENT_ESTIMATION_OVERLAP", "event", AuditStatus.CRITICAL,
            "The estimation window overlaps the event window.", blocks_calculation=True,
            estimation_window=spec.estimation_window.to_dict(), event_window=spec.event_window.to_dict(),
        ))
    return tuple(out)


def validate_parsed_dataset(parsed: ParsedDataset, spec: AnalysisSpecification) -> tuple[AuditResult, ...]:
    audits: list[AuditResult] = []
    rows = parsed.rows
    if len(rows) > MAX_ROWS:
        audits.append(_audit(
            "DATA_TOO_MANY_ROWS", "input", AuditStatus.CRITICAL,
            "v0.1 accepts at most 25,000 rows per analysis.", blocks_calculation=True, n_rows=len(rows),
        ))
    dates: list[date] = []
    date_texts: list[str] = []
    malformed_rows: list[int] = []
    for row in rows:
        try:
            d = date.fromisoformat(row.date_text)
        except ValueError:
            malformed_rows.append(row.source_row)
            continue
        dates.append(d)
        date_texts.append(row.date_text)
    if malformed_rows:
        audits.append(_audit(
            "DATA_INVALID_DATE", "input", AuditStatus.CRITICAL,
            "One or more dates are not valid ISO calendar dates.", blocks_calculation=True,
            source_rows=malformed_rows,
        ))
    if len(date_texts) == len(rows):
        seen: dict[str, list[int]] = {}
        for row in rows:
            seen.setdefault(row.date_text, []).append(row.source_row)
        dup = {d: rr for d, rr in seen.items() if len(rr) > 1}
        if dup:
            audits.append(_audit(
                "DATA_DUPLICATE_DATE", "input", AuditStatus.CRITICAL,
                "Duplicate date observations are not permitted.", blocks_calculation=True,
                duplicates=dup,
            ))
        if any(dates[i] >= dates[i + 1] for i in range(len(dates) - 1)) and not dup:
            audits.append(_audit(
                "DATA_UNSORTED", "input", AuditStatus.CRITICAL,
                "Input dates are not strictly ascending. Sorting requires explicit user approval or a source-data correction.",
                blocks_calculation=True, resolution="explicit_user_sort_or_source_fix", silent_sort_forbidden=True,
            ))
    if spec.return_units in {"decimal", "percent"}:
        invalid_numeric_rows: list[int] = []
        invalid_return_rows: list[int] = []
        extreme_rows: list[int] = []
        for row in rows:
            for text in (row.security_text, row.benchmark_text):
                if text == "":
                    continue
                try:
                    x = float(text)
                except ValueError:
                    invalid_numeric_rows.append(row.source_row)
                    continue
                if not math.isfinite(x):
                    invalid_numeric_rows.append(row.source_row)
            sr = _parse_return(row.security_text, spec.return_units)
            br = _parse_return(row.benchmark_text, spec.return_units)
            for x in (sr, br):
                if math.isfinite(x) and x < -1.0:
                    invalid_return_rows.append(row.source_row)
            if (math.isfinite(sr) and sr > EXTREME_POSITIVE_RETURN_THRESHOLD) or (
                math.isfinite(br) and br > EXTREME_POSITIVE_RETURN_THRESHOLD
            ):
                extreme_rows.append(row.source_row)
        if invalid_numeric_rows:
            audits.append(_audit(
                "DATA_NONFINITE_OR_NONNUMERIC", "input", AuditStatus.CRITICAL,
                "Non-missing return entries must be finite numeric values.", blocks_calculation=True,
                source_rows=sorted(set(invalid_numeric_rows)),
            ))
        if invalid_return_rows:
            audits.append(_audit(
                "DATA_INVALID_SIMPLE_RETURN", "input", AuditStatus.CRITICAL,
                "Simple arithmetic returns below -100% are invalid.", blocks_calculation=True,
                source_rows=sorted(set(invalid_return_rows)),
            ))
        if extreme_rows:
            audits.append(_audit(
                "DATA_EXTREME_RETURN", "input", AuditStatus.WARNING,
                "An unusually large positive return was preserved without automatic winsorization or deletion.",
                blocks_calculation=False, source_rows=sorted(set(extreme_rows)),
                observation_preserved=True, automatic_winsorization=False,
                threshold_decimal=EXTREME_POSITIVE_RETURN_THRESHOLD,
            ))
    return tuple(audits)


def canonicalize_dataset(parsed: ParsedDataset, spec: AnalysisSpecification, *, sort_approved: bool = False) -> CanonicalDataset:
    rows = list(parsed.rows)
    if spec.return_units not in {"decimal", "percent"}:
        raise EFLValidationError("DATA_RETURN_UNITS_REQUIRED", "Return units must be declared before canonicalization.")
    # Validate dates and duplicates first.
    parsed_dates = []
    for row in rows:
        try:
            parsed_dates.append(date.fromisoformat(row.date_text))
        except ValueError as exc:
            raise EFLValidationError("DATA_INVALID_DATE", "Invalid ISO date in input.", {"source_row": row.source_row}) from exc
    if len(set(parsed_dates)) != len(parsed_dates):
        raise EFLValidationError("DATA_DUPLICATE_DATE", "Duplicate dates prevent canonicalization.")
    if any(parsed_dates[i] >= parsed_dates[i + 1] for i in range(len(parsed_dates) - 1)):
        if not sort_approved:
            raise EFLValidationError("DATA_UNSORTED", "Input is unsorted and explicit sort approval was not supplied.")
        rows.sort(key=lambda r: date.fromisoformat(r.date_text))
    sec = []
    bench = []
    dates_out = []
    source_rows = []
    for row in rows:
        for label, text in (("security_return", row.security_text), ("benchmark_return", row.benchmark_text)):
            if text != "":
                try:
                    raw_value = float(text)
                except ValueError as exc:
                    raise EFLValidationError("DATA_NONFINITE_OR_NONNUMERIC", f"{label} contains a nonnumeric value.", {"source_row": row.source_row}) from exc
                if not math.isfinite(raw_value):
                    raise EFLValidationError("DATA_NONFINITE_OR_NONNUMERIC", f"{label} contains a nonfinite value.", {"source_row": row.source_row})
        s = _parse_return(row.security_text, spec.return_units)
        b = _parse_return(row.benchmark_text, spec.return_units)
        if (math.isfinite(s) and s < -1.0) or (math.isfinite(b) and b < -1.0):
            raise EFLValidationError("DATA_INVALID_SIMPLE_RETURN", "Simple return below -100% prevents canonicalization.")
        if (not math.isnan(s) and not math.isfinite(s)) or (not math.isnan(b) and not math.isfinite(b)):
            raise EFLValidationError("DATA_NONFINITE_OR_NONNUMERIC", "Nonfinite return prevents canonicalization.")
        dates_out.append(row.date_text)
        sec.append(s)
        bench.append(b)
        source_rows.append(row.source_row)
    return CanonicalDataset(
        dates=tuple(dates_out),
        security_return=np.asarray(sec, dtype=np.float64),
        benchmark_return=np.asarray(bench, dtype=np.float64),
        source_rows=tuple(source_rows),
        raw_file_hash=raw_file_hash(parsed.raw_bytes),
    )
