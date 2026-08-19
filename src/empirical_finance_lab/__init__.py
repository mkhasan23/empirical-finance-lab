"""Empirical Finance Lab — audit-first empirical-finance research software.

Stage IV implements the validated v0.1 numerical core against the frozen Stage III corpus.
Version 0.1.1 is the governed interoperability/usability patch release line; the
econometric implementation remains anchored to the frozen Stage III/IV authority and
Stage VIII real-data evidence.
"""

__version__ = "0.1.1"

from .engine import run_analysis
from .schema import AnalysisSpecification, AuditResult, AuditStatus
from .reporting import outcome_to_dict

__all__ = ["run_analysis", "outcome_to_dict", "AnalysisSpecification", "AuditResult", "AuditStatus", "__version__"]
