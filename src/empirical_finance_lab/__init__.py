"""Empirical Finance Lab — audit-first empirical-finance research software.

Stage IV implements the validated v0.1 numerical core against the frozen Stage III corpus.
The project remains pre-alpha and is not yet a formal scholarly release.
"""

__version__ = "0.0.0"

from .engine import run_analysis
from .schema import AnalysisSpecification, AuditResult, AuditStatus
from .reporting import outcome_to_dict

__all__ = ["run_analysis", "outcome_to_dict", "AnalysisSpecification", "AuditResult", "AuditStatus", "__version__"]
