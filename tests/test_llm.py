import pytest
from engine.llm import create_llm_provider, LLMProvider


class FakeLLMProvider(LLMProvider):
    def __init__(self, response: str = "fake response"):
        self._response = response

    def complete(self, prompt: str, context: str = "") -> str:
        return self._response


def test_llm_provider_interface():
    provider = FakeLLMProvider("hello")
    result = provider.complete("test prompt", "test context")
    assert result == "hello"


def test_create_llm_provider_claude(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    config = {"llm": {"provider": "claude", "model": "claude-sonnet-4-6", "api_key": "sk-test", "base_url": None}}
    provider = create_llm_provider(config)
    assert provider.__class__.__name__ == "ClaudeProvider"


def test_create_llm_provider_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    config = {"llm": {"provider": "openai", "model": "gpt-4o", "api_key": "sk-test", "base_url": None}}
    provider = create_llm_provider(config)
    assert provider.__class__.__name__ == "OpenAIProvider"


def test_create_llm_provider_local():
    config = {"llm": {"provider": "local", "model": "llama3", "api_key": "", "base_url": "http://localhost:11434/v1"}}
    provider = create_llm_provider(config)
    assert provider.__class__.__name__ == "LocalProvider"


def test_create_llm_provider_unknown_raises():
    config = {"llm": {"provider": "unknown"}}
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_llm_provider(config)
