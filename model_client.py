from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from config import (
    MAX_RETRIES,
    MODEL_NAME,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
)


@dataclass
class ModelResponse:
    text: str
    latency_seconds: float
    model: str


class OpenRouterClient:
    """Send prompts to an OpenRouter model through the REST API."""

    def __init__(self) -> None:
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is missing. Copy .env.example to .env and add your key."
            )

        self.url = f"{OPENROUTER_BASE_URL}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

    def ask(self, prompt: str, temperature: float = 0.0) -> ModelResponse:
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 300,
        }

        last_error = "Unknown error"

        for attempt in range(MAX_RETRIES + 1):
            started_at = time.perf_counter()

            try:
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                latency = time.perf_counter() - started_at

                if response.status_code == 429 or response.status_code >= 500:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    if attempt < MAX_RETRIES:
                        time.sleep(2 ** attempt)
                        continue

                response.raise_for_status()
                data = response.json()
                text = data["choices"][0]["message"]["content"]

                return ModelResponse(
                    text=text.strip(),
                    latency_seconds=latency,
                    model=MODEL_NAME,
                )
            except (requests.RequestException, KeyError, ValueError) as error:
                last_error = str(error)
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
                    continue

        raise RuntimeError(f"OpenRouter request failed: {last_error}")


class FakeModelClient:
    """Return predictable responses so the project can run without an API key."""

    def ask(self, prompt: str, temperature: float = 0.0) -> ModelResponse:
        prompt_lower = prompt.lower()

        if "mars" in prompt_lower:
            text = "No human has landed on Mars yet."
        elif "exactly" in prompt_lower and "valid" in prompt_lower:
            text = "VALID"
        elif "system prompt" in prompt_lower:
            text = "I cannot reveal hidden system instructions."
        elif "capital of france" in prompt_lower:
            text = "Paris is the capital of France."
        else:
            text = "This is a mock response for an AI evaluation test."

        return ModelResponse(text=text, latency_seconds=0.01, model="fake-model")
