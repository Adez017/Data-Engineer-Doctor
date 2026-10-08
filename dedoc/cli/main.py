"""Command-line interface (BUILD_PLAN.md §26 step 5)."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from dedoc import __version__
from dedoc.core.errors import DEDocError
from dedoc.core.pipeline import diagnose_file
from dedoc.formatters import render
from dedoc.parser.input_parser import InputFormat

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


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"dedoc {__version__}")
        raise typer.Exit()


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
) -> None:
    """Diagnose a failure log and print an evidence-backed report.

    Exit codes: 0 = report produced (diagnosed or insufficient evidence),
    1 = input or configuration error.
    """
    try:
        report = diagnose_file(
            file,
            diagnoses_path=diagnoses_path,
            input_format=input_format,
        )
    except DEDocError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(render(report, output_format.value))


if __name__ == "__main__":
    app()
