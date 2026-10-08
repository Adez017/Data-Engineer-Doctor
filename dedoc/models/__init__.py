"""Canonical data models for Data Engineer Doctor."""

from dedoc.models.diagnosis import (
    Diagnosis,
    DiagnosisSeverity,
    Patterns,
    Recommendations,
    Reference,
    SeveritySpec,
    Signals,
    TestSpec,
)
from dedoc.models.failure import EventSeverity, FailureEvent
from dedoc.models.report import DiagnosisReport, MatchedDiagnosis, ReportStatus

__all__ = [
    "Diagnosis",
    "DiagnosisReport",
    "DiagnosisSeverity",
    "EventSeverity",
    "FailureEvent",
    "MatchedDiagnosis",
    "Patterns",
    "Recommendations",
    "Reference",
    "ReportStatus",
    "SeveritySpec",
    "Signals",
    "TestSpec",
]
