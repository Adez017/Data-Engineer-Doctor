"""Security tests: secret redaction in report-bound text (§14)."""

from __future__ import annotations

from dedoc.core.redaction import REDACTED, redact, redact_lines


def test_password_assignment() -> None:
    out = redact("jdbc:postgresql://host/db password=SuperSecret123 user=alice")
    assert "SuperSecret123" not in out
    assert REDACTED in out
    assert "alice" in out


def test_url_credentials() -> None:
    out = redact("failed to connect to https://user:hunter2@db.example.com:5432/x")
    assert "hunter2" not in out
    assert REDACTED in out


def test_bearer_token() -> None:
    out = redact("Authorization: Bearer eyJhbGciOi.abc123signature")
    assert "eyJhbGciOi" not in out.lower().replace("bearer [redacted]", "")
    assert REDACTED in out


def test_authorization_header() -> None:
    out = redact("header Authorization: Basic dXNlcjpwYXNzd29yZA== accepted")
    assert "dXNlcjpwYXNzd29yZA" not in out
    assert REDACTED in out


def test_aws_access_key() -> None:
    out = redact("using AKIAABC123DEF456GHI7 credentials")
    assert "AKIAABC123DEF456GHI7" not in out
    assert REDACTED in out


def test_sas_query_parameter() -> None:
    out = redact("https://acct.dfs.core.windows.net/c?sv=2024&sig=AbCdEf123%3D&se=2025")
    assert "AbCdEf123" not in out
    assert REDACTED in out


def test_private_key_block() -> None:
    out = redact(
        "config:\n-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA\n"
        "-----END RSA PRIVATE KEY-----\nend"
    )
    assert "MIIEpAIBAAKCAQEA" not in out
    assert REDACTED in out


def test_api_key_assignment() -> None:
    out = redact('api_key = "sk-live-9f8e7d6c5b4a"')
    assert "sk-live-9f8e7d6c5b4a" not in out
    assert REDACTED in out


def test_clean_text_unchanged() -> None:
    text = "AnalysisException: Column 'x' cannot be resolved"
    assert redact(text) == text


def test_empty_string() -> None:
    assert redact("") == ""


def test_redact_lines_clamps() -> None:
    out = redact_lines("x" * 500 + "\nshort line")
    first = out.splitlines()[0]
    assert len(first) <= 200
    assert "short line" in out


def test_mixed_log_line() -> None:
    line = (
        "2024-10-08 ERROR conn: url=jdbc:mysql://db:3306/w password=pw123 "
        "token=abc123def456ghi normal text"
    )
    out = redact(line)
    assert "pw123" not in out
    assert "abc123def456ghi" not in out
    assert "normal text" in out
