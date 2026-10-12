"""Report formatters."""

from dedoc.formatters.catalog import format_diagnosis_catalog
from dedoc.formatters.report import format_json, format_markdown, format_text, render

__all__ = [
    "format_diagnosis_catalog",
    "format_json",
    "format_markdown",
    "format_text",
    "render",
]
