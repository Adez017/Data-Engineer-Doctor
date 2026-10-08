"""Report rendering: JSON / Markdown / text (§9 step 11, M1)."""

from __future__ import annotations

import json

from dedoc.evidence.models import ConfidenceBand
from dedoc.models.report import DiagnosisReport, MatchedDiagnosis


def _band_label(band: ConfidenceBand | None) -> str:
    return band.value if band else "n/a"


def format_json(report: DiagnosisReport) -> str:
    return json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False)


def _matched_sections(match: MatchedDiagnosis, style: str) -> list[str]:
    lines: list[str] = []
    entries = [
        ("Matched exception types", match.matched_exception_types),
        ("Matched signals", match.matched_signals),
        ("Hypotheses", match.hypotheses),
    ]
    for label, values in entries:
        if not values:
            continue
        joined = ", ".join(values)
        if style == "markdown":
            lines.append(f"- **{label}:** {joined}")
        else:
            lines.append(f"  {label}: {joined}")
    return lines


def _evidence_lines(match: MatchedDiagnosis, style: str) -> list[str]:
    lines: list[str] = []
    confidence = f"{match.confidence_band.value} ({match.score}/100)"
    if style == "markdown":
        lines.append(f"- **Confidence:** {confidence}")
        if match.evidence:
            lines.append("- **Evidence:**")
            for item in match.evidence:
                lines.append(f"  - `{item.type.value}` {item.description} (+{item.weight})")
                if item.excerpt:
                    lines.append(f"    > {item.excerpt}")
    else:
        lines.append(f"  Confidence: {confidence}")
        if match.evidence:
            lines.append("  Evidence:")
            for item in match.evidence:
                lines.append(f"    - [{item.type.value}] {item.description} (+{item.weight})")
                if item.excerpt:
                    lines.append(f"        > {item.excerpt}")
    return lines


def _recommendation_lines(match: MatchedDiagnosis, style: str) -> list[str]:
    lines: list[str] = []
    rec = match.recommendations
    groups = [
        ("Immediate", rec.immediate),
        ("Recommended", rec.recommended),
        ("Prevention", rec.prevention),
    ]
    for label, items in groups:
        if not items:
            continue
        if style == "markdown":
            lines.append(f"**{label}**")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        else:
            lines.append(f"  {label}:")
            lines.extend(f"    - {item}" for item in items)
    return lines


def format_markdown(report: DiagnosisReport) -> str:
    lines = [
        "# Data Engineer Doctor Report",
        "",
        f"- **Input:** {report.input_source}",
        f"- **Platform:** {report.platform}",
        f"- **Status:** {report.status.value}",
        f"- **Top confidence:** {_band_label(report.top_confidence_band)}",
        f"- **Events:** {report.event_count}",
        f"- **Generated:** {report.generated_at.isoformat()}",
        f"- **DEDoc version:** {report.dedoc_version}",
        "",
        report.message,
    ]
    if report.error_types:
        lines += ["", f"**Observed error types:** {', '.join(report.error_types)}"]
    for match in report.matches:
        lines += [
            "",
            f"## {match.id} — {match.name}",
            "",
            f"- **Category:** {match.category}",
            f"- **Severity:** {match.severity.value}",
            f"- **Platforms:** {', '.join(match.platforms)}",
            *_matched_sections(match, style="markdown"),
            *_evidence_lines(match, style="markdown"),
            "",
        ]
        lines += _recommendation_lines(match, style="markdown")
        if match.references:
            lines.append("**References**")
            lines.extend(f"- [{ref.source}]({ref.url})" for ref in match.references)
            lines.append("")
    return "\n".join(lines).rstrip()


def format_text(report: DiagnosisReport) -> str:
    lines = [
        "Data Engineer Doctor",
        f"Input:     {report.input_source}",
        f"Platform:  {report.platform}",
        f"Status:    {report.status.value}",
        f"Confidence: {_band_label(report.top_confidence_band)}",
        f"Events:    {report.event_count}",
        f"Version:   {report.dedoc_version}",
        "",
        report.message,
    ]
    if report.error_types:
        lines.append(f"Observed error types: {', '.join(report.error_types)}")
    for match in report.matches:
        lines += [
            "",
            f"[{match.id}] {match.name}",
            f"  Category: {match.category} | Severity: {match.severity.value} "
            f"| Platforms: {', '.join(match.platforms)}",
            *_matched_sections(match, style="text"),
            *_evidence_lines(match, style="text"),
        ]
        lines += _recommendation_lines(match, style="text")
        if match.references:
            lines.append("  References:")
            lines.extend(f"    - {ref.source}: {ref.url}" for ref in match.references)
    return "\n".join(lines).rstrip()


def render(report: DiagnosisReport, output_format: str) -> str:
    if output_format == "json":
        return format_json(report)
    if output_format == "markdown":
        return format_markdown(report)
    return format_text(report)
