"""Stable EFL exceptions and error codes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EFLErrorDetail:
    code: str
    message: str
    evidence: dict[str, object] | None = None


class EFLError(Exception):
    """Base exception carrying a stable machine-readable error code."""

    def __init__(self, code: str, message: str, evidence: dict[str, object] | None = None):
        super().__init__(message)
        self.detail = EFLErrorDetail(code=code, message=message, evidence=evidence)

    @property
    def code(self) -> str:
        return self.detail.code


class EFLValidationError(EFLError):
    """Input/specification validation failure."""


class EFLComputationError(EFLError):
    """Numerical computation failure."""
