"""Pure lifecycle guards used by the future browser worker/state machine."""
from __future__ import annotations


def watchdog_decision(elapsed_seconds: float, watchdog_seconds: float = 45.0) -> dict[str, object]:
    if elapsed_seconds > watchdog_seconds:
        return {"state": "FAILED", "error_code": "RUN_TIMEOUT", "partial_result_visible": False}
    return {"state": "RUNNING", "error_code": None, "partial_result_visible": False}


def execution_acceptance(current_execution_id: str, returned_execution_id: str) -> dict[str, object]:
    if current_execution_id != returned_execution_id:
        return {"state": "DISCARDED", "error_code": "RUN_STALE_EXECUTION", "result_visible": False}
    return {"state": "ACCEPTED", "error_code": None, "result_visible": True}
