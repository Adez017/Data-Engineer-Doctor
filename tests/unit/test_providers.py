"""Phase 5 tests: AI provider optionality, redaction, and privacy (BUILD_PLAN.md §13/§14, M5/M6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dedoc.core.errors import ProviderConfigError, ProviderError
from dedoc.models.report import DiagnosisReport
from dedoc.providers.base import ProviderConfig
from dedoc.providers.noop import NullProvider
from dedoc.providers.openai_compat import (
    AzureOpenAIProvider,
    OpenAIProvider,
)
from dedoc.providers.prompt import build_user_prompt
from dedoc.providers.registry import build_provider, provider_config_from_env


def _response(content: str) -> bytes:
    return json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8")


def test_provider_config_rejects_unknown_provider() -> None:
    with pytest.raises(ProviderConfigError):
        ProviderConfig(provider="skynet")


def test_provider_config_rejects_bad_bounds() -> None:
    with pytest.raises(ProviderConfigError):
        ProviderConfig(provider="openai", timeout_seconds=0)
    with pytest.raises(ProviderConfigError):
        ProviderConfig(provider="openai", max_tokens=0)
    with pytest.raises(ProviderConfigError):
        ProviderConfig(provider="openai", temperature=3.0)


def test_none_provider_never_available() -> None:
    provider = build_provider(ProviderConfig(provider="none"))
    assert isinstance(provider, NullProvider)
    assert not provider.available()
    with pytest.raises(ProviderError):
        provider.explain("anything")


def test_openai_unavailable_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEDOC_OPENAI_API_KEY", raising=False)
    provider = build_provider(ProviderConfig(provider="openai", model="gpt-4o-mini"))
    assert not provider.available()


def test_openai_available_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEDOC_OPENAI_API_KEY", "sk-test-not-a-real-key")
    config = ProviderConfig(provider="openai", model="gpt-4o-mini")
    provider = build_provider(config)
    assert provider.available()
    assert provider.name == "openai"


def test_ollama_requires_no_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEDOC_OPENAI_API_KEY", raising=False)
    provider = build_provider(ProviderConfig(provider="ollama", model="llama3.2"))
    assert provider.available()


def test_anthropic_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEDOC_ANTHROPIC_API_KEY", raising=False)
    provider = build_provider(ProviderConfig(provider="anthropic", model="claude-3-5-haiku"))
    assert not provider.available()
    monkeypatch.setenv("DEDOC_ANTHROPIC_API_KEY", "sk-ant-test")
    assert build_provider(
        ProviderConfig(provider="anthropic", model="claude-3-5-haiku")
    ).available()


def test_provider_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEDOC_AI_PROVIDER", "ollama")
    monkeypatch.setenv("DEDOC_AI_MODEL", "llama3.2")
    monkeypatch.setenv("DEDOC_AI_BASE_URL", "http://127.0.0.1:11434/v1")
    config = provider_config_from_env()
    assert config.provider == "ollama"
    assert config.model == "llama3.2"
    assert config.base_url == "http://127.0.0.1:11434/v1"


def test_provider_config_from_env_override_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEDOC_AI_PROVIDER", raising=False)
    with pytest.raises(ProviderConfigError):
        provider_config_from_env(provider="worst-ai")


def test_explain_sends_redacted_body_only() -> None:
    captured: dict[str, object] = {}

    def transport(
        url: str, body: dict[str, object], headers: dict[str, str], timeout: float
    ) -> bytes:
        captured["url"] = url
        captured["body"] = body
        captured["headers"] = headers
        return _response("The executor ran out of heap space.")

    report = DiagnosisReport.model_validate(
        {
            "dedoc_version": "0.1.0",
            "input_source": "input.log",
            "platform": "spark",
            "status": "diagnosed",
            "top_confidence_band": "HIGH",
            "event_count": 1,
            "message": "DEDOC-SPARK-001 selected with HIGH confidence (80/100).",
        }
    )
    # The prompt is the boundary: secrets in the raw log must not survive into
    # the bytes that an external provider would receive.
    prompt = build_user_prompt(
        report,
        "jdbc url=auth password=SuperSecret99 attempt to http://user:pass@db/x",
    )
    provider = OpenAIProvider(
        model="gpt-4o-mini",
        api_key="sk-supplied-secret-key",
        transport=transport,
    )
    out = provider.explain(prompt)

    assert out == "The executor ran out of heap space."
    body = captured["body"]
    assert isinstance(body, dict)
    assert captured["url"].endswith("/chat/completions")
    assert "sk-supplied-secret-key" not in json.dumps(body)
    assert "SuperSecret99" not in json.dumps(body)
    assert "[REDACTED]" in json.dumps(body)
    # the API key travels only in the Authorization header, never in the body
    assert captured["headers"]["Authorization"] == "Bearer sk-supplied-secret-key"


def test_azure_endpoint_and_header() -> None:
    provider = AzureOpenAIProvider(
        model="dedoc-deploy",
        base_url="https://dedoc.openai.azure.com",
        api_key="azure-secret",
    )
    assert provider.available()
    assert provider._endpoint().startswith(
        "https://dedoc.openai.azure.com/openai/deployments/dedoc-deploy/chat/completions"
    )
    assert "api-version=" in provider._endpoint()
    assert provider._headers() == {"api-key": "azure-secret"}


def test_anthropic_body_shape() -> None:
    captured: dict[str, object] = {}

    def transport(
        url: str, body: dict[str, object], headers: dict[str, str], timeout: float
    ) -> bytes:
        captured["url"], captured["body"], captured["headers"] = url, body, headers
        return json.dumps({"content": [{"text": "looks like a driver OOM"}]}).encode("utf-8")

    from dedoc.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(
        model="claude-3-5-haiku", api_key="sk-ant-test", transport=transport
    )
    out = provider.explain("report text")
    assert out == "looks like a driver OOM"
    body = captured["body"]
    assert isinstance(body, dict)
    assert body["model"] == "claude-3-5-haiku"
    assert captured["headers"]["x-api-key"] == "sk-ant-test"
    assert captured["url"].endswith("/v1/messages")


def test_prompt_redacts_secrets() -> None:
    report = DiagnosisReport.model_validate(
        {
            "dedoc_version": "0.1.0",
            "input_source": "input.log",
            "platform": "spark",
            "status": "diagnosed",
            "top_confidence_band": "HIGH",
            "event_count": 1,
            "message": "DEDOC-SPARK-001 selected with HIGH confidence (80/100).",
        }
    )
    text = "jdbc:postgresql://db/x password=Pw!Secret123 token=abc123def45 user=alice"
    prompt = build_user_prompt(report, text)
    assert "Pw!Secret123" not in prompt
    assert "abc123def45" not in prompt
    assert "[REDACTED]" in prompt


def test_pipeline_attaches_ai_explanation_when_available(
    fixtures_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import dedoc.core.pipeline as pipeline
    from dedoc import diagnose

    class _FakeProvider:
        name = "openai"
        model = "fake-model"

        def available(self) -> bool:
            return True

        def explain(self, prompt: str) -> str:
            return "Deterministic evidence strongly supports an executor heap exhaustion."

    monkeypatch.setattr(pipeline, "build_provider", lambda config: _FakeProvider())
    report = diagnose(
        fixtures_dir / "positive" / "spark-executor-oom" / "input.log",
        provider_config=ProviderConfig(provider="openai", model="fake-model"),
    )
    assert report.ai_explanation is not None
    assert report.ai_explanation.provider == "openai"
    assert report.ai_explanation.model == "fake-model"
    assert "heap" in report.ai_explanation.text


def test_pipeline_skips_ai_when_provider_unavailable(
    fixtures_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dedoc import diagnose

    monkeypatch.delenv("DEDOC_OPENAI_API_KEY", raising=False)
    report = diagnose(
        fixtures_dir / "positive" / "spark-executor-oom" / "input.log",
        provider_config=ProviderConfig(provider="openai", model="gpt-4o-mini"),
    )
    assert report.ai_explanation is None


def test_deterministic_default_has_no_ai(fixtures_dir: Path) -> None:
    from dedoc import diagnose

    report = diagnose(fixtures_dir / "positive" / "spark-executor-oom" / "input.log")
    assert report.ai_explanation is None


def test_report_schema_version_is_four() -> None:
    assert DiagnosisReport.model_fields["report_schema_version"].default == "4"
    assert "ai_explanation" in DiagnosisReport.model_fields
