"""Diagnosis report model — the output contract of the deterministic pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from dedoc.agents.models import InvestigationRecord
from dedoc.evidence.models import SCORING_MODEL_VERSION, ConfidenceBand, Evidence
from dedoc.models.diagnosis import (
    DiagnosisSeverity,
    Recommendations,
    Reference,
)


class ReportStatus(StrEnum):
    DIAGNOSED = "diagnosed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class MatchedDiagnosis(BaseModel):
    """A diagnosis matched by the deterministic rules and scored by §10."""

    id: str
    name: str
    category: str
    severity: DiagnosisSeverity
    platforms: list[str]
    score: int = Field(ge=0, le=100)
    confidence_band: ConfidenceBand
    evidence: list[Evidence] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    matched_exception_types: list[str] = Field(default_factory=list)
    matched_signals: list[str] = Field(default_factory=list)
    recommendations: Recommendations = Field(default_factory=Recommendations)
    references: list[Reference] = Field(default_factory=list)


class DiagnosisReport(BaseModel):
    """Structured result of one diagnosis run."""

    dedoc_version: str
    report_schema_version: str = "3"
    scoring_model_version: str = SCORING_MODEL_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input_source: str
    platform: str
    status: ReportStatus
    top_confidence_band: ConfidenceBand | None = None
    event_count: int
    error_types: list[str] = Field(default_factory=list)
    matches: list[MatchedDiagnosis] = Field(default_factory=list)
    message: str = ""
    investigation: InvestigationRecord | None = None
