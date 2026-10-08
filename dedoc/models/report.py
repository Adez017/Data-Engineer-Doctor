"""Diagnosis report model — the output contract of the deterministic pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from dedoc.models.diagnosis import (
    DiagnosisSeverity,
    Recommendations,
    Reference,
)


class ReportStatus(StrEnum):
    DIAGNOSED = "diagnosed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class MatchedDiagnosis(BaseModel):
    """A diagnosis matched by the deterministic rule engine.

    ``matched_*`` fields record *which* rules fired. Evidence scoring and
    confidence bands are added in Phase 3 (BUILD_PLAN.md §10).
    """

    id: str
    name: str
    category: str
    severity: DiagnosisSeverity
    platforms: list[str]
    hypotheses: list[str] = Field(default_factory=list)
    matched_exception_types: list[str] = Field(default_factory=list)
    matched_signals: list[str] = Field(default_factory=list)
    recommendations: Recommendations = Field(default_factory=Recommendations)
    references: list[Reference] = Field(default_factory=list)


class DiagnosisReport(BaseModel):
    """Structured result of one diagnosis run."""

    dedoc_version: str
    report_schema_version: str = "1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input_source: str
    platform: str
    status: ReportStatus
    event_count: int
    error_types: list[str] = Field(default_factory=list)
    matches: list[MatchedDiagnosis] = Field(default_factory=list)
    message: str = ""
