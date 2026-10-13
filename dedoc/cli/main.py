"""Command-line interface (BUILD_PLAN.md §26 step 5)."""

from __future__ import annotations

import json
import sys
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from dedoc import __version__
from dedoc.core.errors import DEDocError, InputError
from dedoc.parser.input_parser import InputFormat

if TYPE_CHECKING:
    from dedoc.tools.context import InvestigationContext

app = typer.Typer(
    name="dedoc",
    help="Data Engineer Doctor — evidence-driven diagnosis for data engineering failures.",
    no_args_is_help=True,
    add_completion=False,
)


class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"


class ListFormat(StrEnum):
    TEXT = "text"
    JSON = "json"


class ColorMode(StrEnum):
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


def _use_color(mode: ColorMode) -> bool:
    if mode is ColorMode.ALWAYS:
        return True
    if mode is ColorMode.NEVER:
        return False
    return bool(sys.stdout.isatty())


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"dedoc {__version__}")
        raise typer.Exit()


def _load_context(path: Path) -> InvestigationContext:
    """Read a YAML/JSON context file into an InvestigationContext."""
    import yaml

    from dedoc.tools.context import context_from_mapping

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"cannot read investigation context: {path}: {exc}") from exc
    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise InputError(f"invalid investigation context YAML/JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError("investigation context must be a mapping")
    return context_from_mapping(data)


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Data Engineer Doctor — evidence-driven diagnosis for data engineering failures."""


@app.command()
def diagnose(
    file: Annotated[Path, typer.Argument(help="Path to a failure log: TXT, JSON, or JSONL.")],
    output_format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format.")
    ] = OutputFormat.TEXT,
    input_format: Annotated[
        InputFormat,
        typer.Option("--input-format", help="Override automatic input format detection."),
    ] = InputFormat.AUTO,
    diagnoses_path: Annotated[
        Path | None, typer.Option("--diagnoses-path", help="Override the diagnoses directory.")
    ] = None,
    investigate: Annotated[
        bool,
        typer.Option(
            "--investigate",
            help="Run the bounded investigation agent over optional structured context.",
        ),
    ] = False,
    context_file: Annotated[
        Path | None,
        typer.Option(
            "--context",
            "-c",
            help="Structured context file (YAML/JSON): runs, schemas, metrics, query plan, logs.",
        ),
    ] = None,
    ai: Annotated[
        bool,
        typer.Option(
            "--ai",
            help="Attach an optional AI explanation. Provider and keys come from the "
            "DEDOC_AI_* environment variables; see the CLI reference.",
        ),
    ] = False,
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider",
            help="Override the AI provider: none, openai, openai_compatible, ollama, "
            "azure_openai, or anthropic.",
        ),
    ] = None,
    ai_model: Annotated[
        str | None,
        typer.Option("--ai-model", help="Override the AI model for the chosen provider."),
    ] = None,
    ai_base_url: Annotated[
        str | None,
        typer.Option("--ai-base-url", help="Override the provider base URL."),
    ] = None,
    color: Annotated[
        ColorMode,
        typer.Option(
            "--color",
            help="Colorize the text report: auto (on a terminal), always, or never.",
        ),
    ] = ColorMode.AUTO,
) -> None:
    """Diagnose a failure log and print an evidence-backed report.

    Exit codes: 0 = report produced (diagnosed or insufficient evidence),
    1 = input or configuration error.
    """
    try:
        from dedoc.core.pipeline import diagnose_file
        from dedoc.formatters import render

        context = _load_context(context_file) if context_file is not None else None
        from dedoc.providers.base import ProviderConfig
        from dedoc.providers.registry import provider_config_from_env

        provider_config: ProviderConfig | None = None
        if ai or provider is not None or ai_model is not None or ai_base_url is not None:
            provider_config = provider_config_from_env(
                provider=provider,
                model=ai_model,
                base_url=ai_base_url,
            )
        report = diagnose_file(
            file,
            diagnoses_path=diagnoses_path,
            input_format=input_format,
            investigate=investigate,
            context=context,
            provider_config=provider_config,
        )
    except DEDocError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(render(report, output_format.value, color=_use_color(color)))


@app.command(name="list-diagnoses")
def list_diagnoses_command(
    output_format: Annotated[
        ListFormat, typer.Option("--format", "-f", help="Output format.")
    ] = ListFormat.TEXT,
    diagnoses_path: Annotated[
        Path | None, typer.Option("--diagnoses-path", help="Override the diagnoses directory.")
    ] = None,
) -> None:
    """List available diagnosis definitions (id, name, category, severity)."""
    from dedoc.diagnosis.loader import load_diagnoses
    from dedoc.formatters import format_diagnosis_catalog

    try:
        diagnoses = load_diagnoses(diagnoses_path)
    except DEDocError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if output_format is ListFormat.JSON:
        rows = [
            {
                "id": d.id,
                "name": d.name,
                "category": d.category,
                "severity": d.severity.default,
                "platforms": list(d.platforms),
            }
            for d in diagnoses.values()
        ]
        typer.echo(json.dumps(rows, indent=2))
        return
    typer.echo(format_diagnosis_catalog(diagnoses))


if __name__ == "__main__":
    app()
