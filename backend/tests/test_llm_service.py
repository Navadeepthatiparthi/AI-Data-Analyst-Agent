import pytest

from app.services.llm_service import LLMService


def test_llm_service_reads_configuration(monkeypatch):
    monkeypatch.setenv(
        "LLM_API_KEY",
        "local",
    )

    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    )

    monkeypatch.setenv(
        "LLM_MODEL",
        "qwen3:4b",
    )

    service = LLMService()

    assert service.api_key == "local"
    assert service.base_url == (
        "http://localhost:11434/v1"
    )
    assert service.model == "qwen3:4b"


def test_llm_service_defaults_to_local_ollama(
    monkeypatch,
):
    monkeypatch.delenv(
        "LLM_API_KEY",
        raising=False,
    )

    monkeypatch.delenv(
        "LLM_BASE_URL",
        raising=False,
    )

    monkeypatch.delenv(
        "LLM_MODEL",
        raising=False,
    )

    service = LLMService()

    assert service.api_key == "local"

    assert service.base_url == (
        "http://localhost:11434/v1"
    )

    assert service.model == "qwen3:4b"


@pytest.mark.asyncio
async def test_llm_service_rejects_empty_prompt(
    monkeypatch,
):
    monkeypatch.setenv(
        "LLM_API_KEY",
        "local",
    )

    service = LLMService()

    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty.",
    ):
        await service.generate("   ")