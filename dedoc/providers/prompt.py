"""Prompt construction for optional AI explanations (§13, §14).

Everything that reaches a provider is built from already-redacted report data
plus a re-redacted, bounded excerpt of the original input. The prompt explicitly
forbids inventing facts and demands an abstention when evidence is insufficient.
"""

from __future__ import annotations

from dedoc.core.redaction import redact_lines
from dedoc.models.report import DiagnosisReport

SYSTEM_INSTRUCTIONS = (
    "You are Data Engineer Doctor, an evidence-driven diagnostic assistant. "
    "Explain the diagnosis using ONLY the evidence provided in the prompt.\n"
    "Rules:\n"
    "- Base every claim on the cited evidence; never invent log lines, errors, or facts.\n"
    "- If the evidence is insufficient to explain the failure, say so explicitly.\n"
    "- Keep the explanation to at most 200 words.\n"
    "- The input is already redacted; if you see placeholder text like [REDACTED], "
    "treat it as a sensitive value and do not try to guess or reveal it.\n"
    "- Do not recommend destructive actions; suggestions must be safe and reversible."
)

_MAX_INPUT_CHARS = 6000


def _format_match_lines(report: DiagnosisReport) -> list[str]:
    lines: list[str] = []
    for match in report.matches[:3]:
        lines.append(f"- {match.id} {match.name} ({match.confidence_band.value} {match.score}/100)")
        if match.matched_signals:
            lines.append(f"  signals: {', '.join(match.matched_signals)}")
        if match.hypotheses:
            lines.append(f"  hypotheses: {', '.join(match.hypotheses)}")
        for item in match.evidence[:4]:
            excerpt = item.excerpt or ""
            if excerpt:
                lines.append(f"  evidence: [{item.type.value}] {item.description} — {excerpt}")
            else:
                lines.append(f"  evidence: [{item.type.value}] {item.description}")
        if match.recommendations.recommended:
            lines.append(f"  recommended: {'; '.join(match.recommendations.recommended)}")
    return lines


def build_user_prompt(report: DiagnosisReport, input_text: str) -> str:
    """Build the user prompt from a report and the (un)redacted input text."""
    excerpt = redact_lines(input_text, max_line=300)[:_MAX_INPUT_CHARS]
    top_band = report.top_confidence_band.value if report.top_confidence_band else "n/a"
    blocks: list[str] = [
        "## Failure report",
        f"Status: {report.status.value}",
        f"Top confidence: {top_band}",
        f"Report message: {report.message}",
        "",
        "## Matched diagnoses",
        *(report.matches and _format_match_lines(report) or ["(no diagnosis matched)"]),
    ]
    if report.investigation is not None:
        blocks += [
            "",
            "## Investigation findings",
            f"Status: {report.investigation.status.value}; reason: {report.investigation.reason}",
            *(
                f"- {f.kind.value} ({f.tool}): {f.description}"
                for f in report.investigation.findings
            ),
            *(f"- contradiction: {c.description}" for c in report.investigation.contradictions),
        ]
    blocks += [
        "",
        "## Input excerpt (redacted)",
        excerpt or "(empty)",
    ]
    return "\n".join(blocks)


__all__ = ["SYSTEM_INSTRUCTIONS", "build_user_prompt"]
