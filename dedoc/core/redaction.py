"""Secret and credential redaction (BUILD_PLAN.md §14).

Redaction runs on any log-derived text that could reach a report, an external
provider, or telemetry. Default posture: local analysis, redact before export.
"""

from __future__ import annotations

import re

REDACTED = "[REDACTED]"

#: Ordered patterns; first replacement wins per span, later patterns clean leftovers.
_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Private key blocks (multi-line)
    (
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        REDACTED,
    ),
    # Authorization / proxy-authorization headers
    (
        re.compile(r"(?i)\b(authorization|proxy-authorization)\s*:\s*\S+(?:\s+\S+)?"),
        r"\1: " + REDACTED,
    ),
    # AWS access key ids
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), REDACTED),
    # Databricks PAT-style tokens
    (re.compile(r"\bdapi[0-9a-fA-F]{16,}\b"), REDACTED),
    # Bearer / token tokens
    (re.compile(r"(?i)\b(bearer|token)\s+([A-Za-z0-9._~+/=-]{8,})"), r"\1 " + REDACTED),
    # key=value / key: value credentials (password, secret, token, api_key, ...)
    (
        re.compile(
            r"(?i)\b((?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key"
            r"|secret[_-]?key|client[_-]?secret|shared[_-]?access[_-]?key|sas[_-]?key)"
            r"\s*[=:]\s*)(\"[^\"]*\"|'[^']*'|\S+)"
        ),
        r"\1" + REDACTED,
    ),
    # URLs with credentials in the authority component (scheme://user:pass@host)
    (
        re.compile(r"\b([a-z][a-z0-9+.-]*://)[^/\s:@]+:[^/\s@]+@", re.IGNORECASE),
        r"\1" + REDACTED + "@",
    ),
    # URLs with secret-bearing query parameters (SAS, sig, token, key, ...)
    (
        re.compile(
            r"(?i)([?&](?:sig|signature|sv|se|sp|st|sas|token|access_token|key"
            r"|api_key|apikey|auth)=)[^&\s\"']+"
        ),
        r"\1" + REDACTED,
    ),
)


def redact(text: str) -> str:
    """Return ``text`` with credentials, keys, and tokens replaced."""
    if not text:
        return text
    result = text
    for pattern, replacement in _PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def redact_lines(text: str, max_line: int = 200) -> str:
    """Redact and clamp each line — used for evidence excerpts."""
    lines = [redact(line)[:max_line] for line in text.splitlines()]
    return "\n".join(lines)
