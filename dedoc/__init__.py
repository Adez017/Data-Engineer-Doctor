"""Data Engineer Doctor (DEDoc) — evidence-driven diagnosis for data engineering failures.

Public Python SDK. Everything in ``dedoc.*`` other than the names in
``__all__`` is an internal implementation detail; the CLI is ``dedoc diagnose``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dedoc.agents.config import AgentConfig
    from dedoc.agents.models import InvestigationRecord
    from dedoc.models.diagnosis import Diagnosis
    from dedoc.models.report import AIExplanation, DiagnosisReport
    from dedoc.parser.input_parser import InputFormat
    from dedoc.providers.base import ProviderConfig
    from dedoc.tools.context import InvestigationContext

__all__ = [
    "__version__",
    "AgentConfig",
    "AIExplanation",
    "Diagnosis",
    "DiagnosisReport",
    "InvestigationContext",
    "InvestigationRecord",
    "ProviderConfig",
    "diagnose",
    "list_diagnoses",
]


def _read_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("data-engineer-doctor")
    except PackageNotFoundError:
        return "0.0.0+local"


__version__ = _read_version()


def list_diagnoses(diagnoses_path: str | Path | None = None) -> list[Diagnosis]:
    """Return all loaded diagnosis definitions, sorted by id (BUILD_PLAN.md §6)."""
    from dedoc.diagnosis.loader import load_diagnoses

    return list(load_diagnoses(diagnoses_path).values())


def diagnose(
    source: str | Path,
    *,
    diagnoses_path: str | Path | None = None,
    input_format: InputFormat | None = None,
    investigate: bool = False,
    context: InvestigationContext | None = None,
    agent_config: AgentConfig | None = None,
    ai: bool = False,
    provider_config: ProviderConfig | None = None,
) -> DiagnosisReport:
    """Run the diagnosis pipeline on a failure log file.

    Args:
        source: path to a failure log (TXT, JSON, or JSONL).
        diagnoses_path: optional override for the diagnoses directory.
        input_format: optional ``InputFormat`` override (defaults to auto-detect).
        investigate: when True, run the bounded investigation agent (§11) over
            ``context`` and attach its findings to the report.
        context: optional structured context (runs/schemas/metrics/query
            plan/logs) that the tools read from.
        agent_config: optional hard limits for the investigation agent.
        ai: when True and a provider is configured (env `DEDOC_AI_PROVIDER` or
            ``provider_config``), attach an optional AI explanation (§13).
        provider_config: optional explicit provider configuration; takes
            precedence over the environment when AI is enabled.

    Returns:
        An evidence-backed ``DiagnosisReport`` (matches, score, confidence band,
        optional investigation and AI explanation).

    Raises:
        InputError: if the input file is missing or malformed.
        DiagnosisLoadError: if diagnosis knowledge cannot be loaded.
        ProviderConfigError: if an explicitly configured provider is invalid.
        ProviderError: if an explicitly enabled AI provider fails.
    """
    from dedoc.core.pipeline import diagnose_file
    from dedoc.parser.input_parser import InputFormat
    from dedoc.providers.registry import provider_config_from_env

    if input_format is None:
        input_format = InputFormat.AUTO
    if provider_config is not None:
        resolved_provider = provider_config
    elif ai:
        resolved_provider = provider_config_from_env()
    else:
        resolved_provider = None
    return diagnose_file(
        Path(source),
        diagnoses_path=diagnoses_path,
        input_format=input_format,
        investigate=investigate,
        context=context,
        agent_config=agent_config,
        provider_config=resolved_provider,
    )
