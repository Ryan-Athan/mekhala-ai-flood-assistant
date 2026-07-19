from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class LLMResult:
    ok: bool
    text: str
    provider: str
    error: str | None = None


class OptionalLLMClient:
    """Optional LLM client.

    The app works without any API key. When an API key or local LLM is configured,
    this client can generate more natural ChatGPT-like answers from retrieved context.

    Supported provider values via FLOODMIND_LLM_PROVIDER:
    - none: disable LLM and use local RAG template fallback
    - openai_compatible: use an OpenAI-compatible /v1/chat/completions endpoint
    - openrouter: use OpenRouter chat completions
    - ollama: use a local Ollama model through localhost
    """

    def __init__(self) -> None:
        self.provider = os.getenv("FLOODMIND_LLM_PROVIDER", "none").strip().lower()
        self.timeout = int(os.getenv("FLOODMIND_LLM_TIMEOUT", "20"))

    def generate(self, prompt: str, system_prompt: str) -> LLMResult:
        if self.provider in {"", "none", "disabled"}:
            return LLMResult(ok=False, text="", provider="none", error="LLM disabled")

        if self.provider == "openai_compatible":
            return self._generate_openai_compatible(prompt, system_prompt)

        if self.provider == "openrouter":
            return self._generate_openrouter(prompt, system_prompt)

        if self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt)

        return LLMResult(ok=False, text="", provider=self.provider, error=f"Unknown provider: {self.provider}")

    def _generate_openai_compatible(self, prompt: str, system_prompt: str) -> LLMResult:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not api_key:
            return LLMResult(ok=False, text="", provider="openai_compatible", error="OPENAI_API_KEY not set")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.35,
            "max_tokens": 500,
        }

        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()
            return LLMResult(ok=True, text=text, provider="openai_compatible")
        except Exception as exc:
            return LLMResult(ok=False, text="", provider="openai_compatible", error=str(exc))

    def _generate_openrouter(self, prompt: str, system_prompt: str) -> LLMResult:
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

        if not api_key:
            return LLMResult(ok=False, text="", provider="openrouter", error="OPENROUTER_API_KEY not set")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.35,
            "max_tokens": 500,
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()
            return LLMResult(ok=True, text=text, provider="openrouter")
        except Exception as exc:
            return LLMResult(ok=False, text="", provider="openrouter", error=str(exc))

    def _generate_ollama(self, prompt: str, system_prompt: str) -> LLMResult:
        endpoint = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.35},
        }

        try:
            response = requests.post(f"{endpoint}/api/chat", json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            text = data.get("message", {}).get("content", "").strip()
            if not text:
                return LLMResult(ok=False, text="", provider="ollama", error="Empty Ollama response")
            return LLMResult(ok=True, text=text, provider="ollama")
        except Exception as exc:
            return LLMResult(ok=False, text="", provider="ollama", error=str(exc))
