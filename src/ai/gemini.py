from __future__ import annotations

from urllib.parse import quote

import requests


class GeminiClient:
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str, model: str, timeout: int = 60) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("Required environment variable is missing: GEMINI_API_KEY")

        model = quote(self.model, safe="")
        response = requests.post(
            f"{self.API_BASE}/{model}:generateContent",
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {
                    "parts": [{"text": system_prompt}],
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": user_prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
                },
            },
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Gemini API request failed ({response.status_code}): "
                f"{response.text[:1000]}"
            ) from exc

        try:
            candidates = response.json()["candidates"]
            parts = candidates[0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise RuntimeError("Gemini API returned an unexpected response") from exc
        if not text:
            raise RuntimeError("Gemini API returned an empty summary")
        return text
