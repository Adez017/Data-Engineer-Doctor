"""Report rendering: JSON / Markdown / text (§9 step 11, M1)."""

from __future__ import annotations

import json

from dedoc.agents.models import InvestigationRecord
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


def _investigation_markdown(record: InvestigationRecord) -> list[str]:
    lines = [
        "",
        "## Investigation",
        "",
        f"- **Status:** {record.status.value}",
        f"- **Iterations:** {record.iterations} (budget {record.max_iterations})",
        f"- **Tool calls:** {record.tool_calls} (budget {record.max_tool_calls})",
        f"- **Reason:** {record.reason}",
    ]
    for finding in record.findings:
        lines.append(f"- **{finding.kind.value} finding** ({finding.tool}): {finding.description}")
    for contradiction in record.contradictions:
        lines.append(f"- **Contradiction:** {contradiction.description}")
    if record.calls:
        lines.append("*Tool calls:*")
        for call in record.calls:
            lines.append(f"- `{call.tool}` -> `{call.status.value}`: {call.summary}")
    lines.append("")
    return lines


def _investigation_text(record: InvestigationRecord) -> list[str]:
    lines = [
        "",
        f"Investigation: {record.status.value}",
        f"  Iterations: {record.iterations} (budget {record.max_iterations})"
        f" | Tool calls: {record.tool_calls} (budget {record.max_tool_calls})",
        f"  Reason: {record.reason}",
    ]
    for finding in record.findings:
        lines.append(f"  [finding: {finding.kind.value}] ({finding.tool}) {finding.description}")
    for contradiction in record.contradictions:
        lines.append(f"  [contradiction] {contradiction.description}")
    if record.calls:
        lines.append("  Tool calls:")
        for call in record.calls:
            lines.append(f"    - {call.tool}: {call.status.value} — {call.summary}")
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
    if report.investigation is not None:
        lines += _investigation_markdown(report.investigation)
    return "\n".join(lines).rstrip()


def _text_scoreboard(report: DiagnosisReport) -> list[str]:
    """Ranked one-liner for every candidate (only when ranking matters)."""
    if len(report.matches) < 2:
        return []
    name_width = max(len(match.name) for match in report.matches)
    lines = ["Candidate scoreboard:"]
    for rank, match in enumerate(report.matches, start=1):
        lines.append(
            f"  #{rank}  {match.id:<18} {match.name:<{name_width}} "
            f"{match.confidence_band.value:<6} {match.score:>3}/100"
        )
    return lines + [""]


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
    lines += _text_scoreboard(report)
    if not report.matches:
        return "\n".join(lines).rstrip()

    top, *alternatives = report.matches
    lines += [
        "",
        f"Diagnosis: {top.id} {top.name}",
        f"  Category: {top.category} | Severity: {top.severity.value} "
        f"| Platforms: {', '.join(top.platforms)}",
        *_matched_sections(top, style="text"),
        *_evidence_lines(top, style="text"),
    ]
    lines += _recommendation_lines(top, style="text")
    if top.references:
        lines.append("  References:")
        lines.extend(f"    - {ref.source}: {ref.url}" for ref in top.references)
    if alternatives:
        lines.append("")
        lines.append("  Other candidates considered:")
        for match in alternatives:
            lines.append(
                f"    - {match.id} {match.name} — {match.confidence_band.value} ({match.score}/100)"
            )
    if report.investigation is not None:
        lines += _investigation_text(report.investigation)
    return "\n".join(lines).rstrip()


def render(report: DiagnosisReport, output_format: str) -> str:
    if output_format == "json":
        return format_json(report)
    if output_format == "markdown":
        return format_markdown(report)
    return format_text(report)
