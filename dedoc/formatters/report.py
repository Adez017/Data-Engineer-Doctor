"""Report rendering: JSON / Markdown / text (§9 step 11, M1).

The text renderer leads with the conclusion ("what we found"), then the actions
("what to do next"), then the evidence ("why we think so") so a user can act
without reading the whole report. Internal keys (signals, hypotheses) are shown
in plain language; machine-facing detail lives in the JSON output.
"""

from __future__ import annotations

import json

from dedoc.agents.models import InvestigationRecord
from dedoc.evidence.models import ConfidenceBand
from dedoc.models.report import DiagnosisReport, MatchedDiagnosis, ReportStatus

_GREEN = "\x1b[32m"
_YELLOW = "\x1b[33m"
_RED = "\x1b[31m"
_RESET = "\x1b[0m"

_BAND_COLOR: dict[str, str] = {
    ConfidenceBand.HIGH.value: _GREEN,
    ConfidenceBand.MEDIUM.value: _YELLOW,
    ConfidenceBand.LOW.value: _RED,
}

#: Word expansions so snake_case keys read as plain language ("executor_oom" -> "Executor OOM").
_HUMAN_WORDS = {
    "oom": "OOM",
    "sql": "SQL",
    "api": "API",
    "uri": "URI",
    "dns": "DNS",
    "sas": "SAS",
    "id": "ID",
    "pat": "PAT",
    "dfs": "DFS",
}


def _wrap(text: str, code: str, enabled: bool) -> str:
    return f"{code}{text}{_RESET}" if enabled and code else text


def _humanize(key: str) -> str:
    words = [w for w in (_HUMAN_WORDS.get(part, part.capitalize()) for part in key.split("_")) if w]
    if not words:
        return key
    label = " ".join(words)
    return label[0].upper() + label[1:]


def _band_label(band: ConfidenceBand | None) -> str:
    return band.value if band else "n/a"


def format_json(report: DiagnosisReport) -> str:
    return json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False)


def _first_excerpt(excerpt: str | None) -> str:
    """First line of a contextual excerpt, clamped for readability."""
    if not excerpt:
        return ""
    return excerpt.split(" | ")[0].strip()[:160]


def _matched_markdown_sections(match: MatchedDiagnosis) -> list[str]:
    lines: list[str] = []
    entries = [
        ("Matched exception types", match.matched_exception_types),
        ("Matched signals", [_humanize(s) for s in match.matched_signals]),
        ("Possible causes", [_humanize(h) for h in match.hypotheses]),
    ]
    for label, values in entries:
        if values:
            lines.append(f"- **{label}:** {', '.join(values)}")
    return lines


def _evidence_markdown_lines(match: MatchedDiagnosis) -> list[str]:
    lines = ["", "### Evidence:"]
    if not match.evidence:
        lines += ["", "No observable evidence recorded."]
        return lines
    seen: dict[str, int] = {}
    for rank, item in enumerate(match.evidence, start=1):
        lines += ["", f"{rank}. **{item.description}** (+{item.weight})"]
        first_line = _first_excerpt(item.excerpt)
        if first_line:
            if first_line not in seen:
                seen[first_line] = rank
                lines.append(f"   > {first_line}")
            else:
                lines.append(f"   > (same lines as evidence item {seen[first_line]})")
        else:
            lines.append(f"   > source: {item.source}")
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


def _ai_explanation_str(provider: str, model: str | None) -> str:
    return f"{provider}" if model is None else f"{provider} ({model})"


def _ai_markdown(report: DiagnosisReport) -> list[str]:
    ai = report.ai_explanation
    if ai is None:
        return []
    return [
        "",
        "## AI explanation",
        "",
        f"> Generated by {_ai_explanation_str(ai.provider, ai.model)}",
        "",
        *[f"> {line}" if line else ">" for line in ai.text.splitlines()],
        "",
    ]


def _ai_text(report: DiagnosisReport) -> list[str]:
    ai = report.ai_explanation
    if ai is None:
        return []
    indented = "\n".join(f"    {line}" if line else "" for line in ai.text.splitlines())
    return [
        "",
        f"AI explanation [{_ai_explanation_str(ai.provider, ai.model)}]:",
        indented,
    ]


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
            f"- **Severity:** {match.severity.value}",
            f"- **Platforms:** {', '.join(match.platforms)}",
            f"- **Category:** {match.category}",
            f"- **Confidence:** {match.confidence_band.value} ({match.score}/100)",
            *_matched_markdown_sections(match),
            *_evidence_markdown_lines(match),
            "",
            "### What to do next",
        ]
        lines += _recommendation_lines(match, style="markdown")
        if match.references:
            lines += ["### References", ""]
            lines.extend(f"- [{ref.source}]({ref.url})" for ref in match.references)
            lines.append("")
    if report.investigation is not None:
        lines += _investigation_markdown(report.investigation)
    if report.ai_explanation is not None:
        lines += _ai_markdown(report)
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


def _evidence_text_lines(match: MatchedDiagnosis) -> list[str]:
    """Compact, deduplicated evidence ("why we think so")."""
    lines = ["Evidence:"]
    if not match.evidence:
        lines.append("  No observable evidence recorded.")
        return lines
    seen_excerpts: dict[str, int] = {}
    for rank, item in enumerate(match.evidence, start=1):
        lines.append(f"  {rank}. {item.description} (+{item.weight})")
        first_line = _first_excerpt(item.excerpt)
        if first_line:
            if first_line not in seen_excerpts:
                seen_excerpts[first_line] = rank
                lines.append(f"      > {first_line}")
            else:
                lines.append(f"      > (same lines as evidence item {seen_excerpts[first_line]})")
        else:
            lines.append(f"      > source: {item.source}")
    return lines


def _matched_text_sections(match: MatchedDiagnosis) -> list[str]:
    """Plain-language match provenance for the top candidate."""
    lines = [
        f"  Matched exception types: {', '.join(match.matched_exception_types) or 'n/a'}",
        f"  Matched signals: {', '.join(_humanize(s) for s in match.matched_signals) or 'n/a'}",
    ]
    if match.hypotheses:
        lines.append(f"  Possible causes: {'; '.join(_humanize(h) for h in match.hypotheses)}")
    return lines


def format_text(report: DiagnosisReport, color: bool = False) -> str:
    top_band = report.top_confidence_band
    band_color = _BAND_COLOR.get(top_band.value, "") if top_band else ""
    status = report.status.value if report.status else "n/a"
    status_code = _GREEN if report.status is ReportStatus.DIAGNOSED else _YELLOW
    lines = [
        "Data Engineer Doctor",
        f"Input:     {report.input_source}",
        f"Platform:  {report.platform}",
        f"Status:    {_wrap(status, status_code, color)}",
        f"Confidence: {_wrap(_band_label(top_band), band_color, color)}",
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
    top_band_color = _BAND_COLOR.get(top.confidence_band.value, "")
    lines += [
        "",
        "What we found:",
        f"  {top.id} {top.name}",
        f"  Severity: {top.severity.value} | Platforms: {', '.join(top.platforms)}",
        "  Confidence: "
        f"{_wrap(top.confidence_band.value, top_band_color, color)} "
        f"({top.score}/100)",
    ]
    lines += _matched_text_sections(top)
    lines += [""] + _evidence_text_lines(top)
    rec = top.recommendations
    if rec.immediate or rec.recommended or rec.prevention:
        lines += ["", "What to do next:"]
        lines += _recommendation_lines(top, style="text")
    if top.references:
        lines += ["", "  References:"]
        lines.extend(f"    - {ref.source}: {ref.url}" for ref in top.references)
    if alternatives:
        lines += ["", "  Other candidates considered:"]
        for match in alternatives:
            lines.append(
                f"    - {match.id} {match.name} — {match.confidence_band.value} ({match.score}/100)"
            )
    if report.investigation is not None:
        lines += _investigation_text(report.investigation)
    if report.ai_explanation is not None:
        lines += _ai_text(report)
    return "\n".join(lines).rstrip()


def render(report: DiagnosisReport, output_format: str, color: bool = False) -> str:
    if output_format == "json":
        return format_json(report)
    if output_format == "markdown":
        return format_markdown(report)
    return format_text(report, color=color)
