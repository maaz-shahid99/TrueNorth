"""Evaluation harness (PL-4): golden decision set, grader, and runner."""

from __future__ import annotations

from .fakes import ScriptedGateway
from .golden import GOLDEN_CASES, GoldenCase
from .grader import CaseResult, CheckResult, grade_case
from .runner import EvalReport, run_eval

__all__ = [
    "GOLDEN_CASES",
    "GoldenCase",
    "CaseResult",
    "CheckResult",
    "EvalReport",
    "ScriptedGateway",
    "grade_case",
    "run_eval",
]
