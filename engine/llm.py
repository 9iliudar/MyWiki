from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, context: str = "") -> str:
        ...


class ClaudeProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, base_url: str = None):
        import anthropic
        kwargs = {"api_key": api_key, "timeout": 120.0}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = anthropic.Anthropic(**kwargs)
        self.model = model

    def complete(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": "我已阅读上述内容，请告诉我需要做什么。"})
        messages.append({"role": "user", "content": prompt})
        # Use streaming to avoid gateway timeouts on third-party proxies
        result = []
        with self.client.messages.stream(model=self.model, max_tokens=8192, messages=messages) as stream:
            for text in stream.text_stream:
                result.append(text)
        return "".join(result)


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, base_url: str = None):
        import openai
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = openai.OpenAI(**kwargs)
        self.model = model

    def complete(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        return response.choices[0].message.content


class LocalProvider(LLMProvider):
    def __init__(self, model: str, base_url: str, api_key: str = ""):
        import openai
        self.client = openai.OpenAI(api_key=api_key or "not-needed", base_url=base_url)
        self.model = model

    def complete(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        return response.choices[0].message.content


def create_llm_provider(config: dict) -> LLMProvider:
    llm_config = config["llm"]
    provider = llm_config["provider"]
    if provider == "claude":
        return ClaudeProvider(model=llm_config["model"], api_key=llm_config.get("api_key", ""), base_url=llm_config.get("base_url"))
    elif provider == "openai":
        return OpenAIProvider(model=llm_config["model"], api_key=llm_config.get("api_key", ""), base_url=llm_config.get("base_url"))
    elif provider == "local":
        return LocalProvider(model=llm_config["model"], base_url=llm_config.get("base_url", "http://localhost:11434/v1"), api_key=llm_config.get("api_key", ""))
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
