import json
import requests
from typing import Any

class LLMError(RuntimeError):
    pass

class LLM:
    def __init__(self, settings):
        self.settings = settings

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
        provider = self.settings.llm_provider.lower()
        if provider == "ollama":
            return self._ollama(messages, tools)
        if provider == "openai":
            return self._openai(messages, tools)
        raise LLMError(f"Unknown LLM provider: {provider}")

    def _ollama(self, messages, tools):
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        r = requests.post(
            self.settings.ollama_base_url.rstrip("/") + "/api/chat",
            json=payload,
            timeout=180,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("message", {})

    def _openai(self, messages, tools):
        if not self.settings.openai_api_key:
            raise LLMError("DMC_OPENAI_API_KEY is missing.")
        base = self.settings.openai_base_url.rstrip("/") or "https://api.openai.com/v1"
        payload = {
            "model": self.settings.openai_model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        r = requests.post(
            base + "/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=180,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]
