"""Investigation context: structured data the tools read from (§12).

The deterministic engine works on the input file alone. When structured
runtime context exists — pipeline runs, schema snapshots, metrics, query
plans, additional logs — it is passed in through ``InvestigationContext``
and made available to the read-only tool layer. Missing data is reported as
``UNAVAILABLE``; the agent abstains rather than guessing.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from dedoc.core.errors import InputError
from dedoc.models.failure import FailureEvent


class PipelineRun(BaseModel):
    """One pipeline run observed via a run-history tool."""

    run_id: str
    status: str = "unknown"
    job: str | None = None
    stage: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class SchemaSnapshot(BaseModel):
    """A table schema as seen by get_schema / compare_schema."""

    table: str
    columns: list[str] = Field(default_factory=list)
    data_types: dict[str, str] = Field(default_factory=dict)


class MetricsSample(BaseModel):
    """A single value metric; labels carry the scope (stage/executor)."""

    name: str
    value: float
    unit: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    window: str | None = None


class InvestigationContext(BaseModel):
    """All structured context available to the investigation agent."""

    events: list[FailureEvent] = Field(default_factory=list)
    text: str = ""
    current_run: PipelineRun | None = None
    previous_runs: list[PipelineRun] = Field(default_factory=list)
    schemas: dict[str, SchemaSnapshot] = Field(default_factory=dict)
    metrics: dict[str, MetricsSample] = Field(default_factory=dict)
    query_plan: str | None = None
    log_lines: list[str] = Field(default_factory=list)

    def has_external_data(self) -> bool:
        """True when context carries data beyond the input events/text."""
        return bool(
            self.current_run
            or self.previous_runs
            or self.schemas
            or self.metrics
            or self.query_plan
            or self.log_lines
        )


def context_from_mapping(data: Mapping[str, Any]) -> InvestigationContext:
    """Build a context from a mapping (used by ``--context`` and the SDK).

    Tolerates convenient aliases: ``runs`` -> ``previous_runs``, ``logs`` ->
    ``log_lines``; bare strings are coerced to ``run_id`` / ``table`` / ``name``
    fields.

    Raises:
        InputError: if the mapping cannot be validated.
    """
    source = dict(data)

    def _run(value: Any, run_id: str | None = None) -> Any:
        if isinstance(value, str):
            return {"run_id": value}
        if not isinstance(value, dict):
            raise ValueError(f"{run_id or value!r} is not a run mapping or run id")
        item = dict(value)
        item.setdefault("run_id", run_id or "")
        return item

    def _schema(key: str, value: Any) -> Any:
        if not isinstance(value, dict):
            raise ValueError(f"schema {key!r} must be a mapping")
        item = dict(value)
        item.setdefault("table", key)
        return item

    def _metric(key: str, value: Any) -> Any:
        if isinstance(value, (int, float)):
            return {"name": key, "value": float(value)}
        if not isinstance(value, dict):
            raise ValueError(f"metric {key!r} must be a number or a mapping")
        item = dict(value)
        item.setdefault("name", key)
        return item

    try:
        if "runs" in source and "previous_runs" not in source:
            source["previous_runs"] = source.pop("runs")
        if "logs" in source and "log_lines" not in source:
            source["log_lines"] = source.pop("logs")
        if "current_run" in source and source["current_run"] is not None:
            source["current_run"] = _run(source["current_run"])
        previous = source.get("previous_runs") or []
        source["previous_runs"] = [_run(item) for item in previous]
        schemas = source.get("schemas") or {}
        source["schemas"] = {str(key): _schema(str(key), value) for key, value in schemas.items()}
        metrics = source.get("metrics") or {}
        source["metrics"] = {str(key): _metric(str(key), value) for key, value in metrics.items()}
        source.setdefault("text", "")
        try:
            return InvestigationContext.model_validate(source)
        except ValidationError as exc:
            detail = "; ".join(
                f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
            )
            raise InputError(f"invalid investigation context: {detail}") from exc
    except ValueError as exc:
        raise InputError(f"invalid investigation context: {exc}") from exc


__all__ = [
    "InvestigationContext",
    "MetricsSample",
    "PipelineRun",
    "SchemaSnapshot",
    "context_from_mapping",
]
