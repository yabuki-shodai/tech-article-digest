from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    github_token: str
    repository: str
    issue_number: int
    issue_body: str
    gemini_api_key: str
    gemini_model: str = "gemini-3.5-flash"

    @classmethod
    def from_environment(cls) -> "Settings":
        event = _load_github_event()
        repository = _required_nested_string(event, "repository", "full_name")
        issue = event.get("issue")
        if not isinstance(issue, dict):
            raise ValueError("GitHub event does not contain an issue")

        issue_number = issue.get("number")
        if not isinstance(issue_number, int):
            raise ValueError("GitHub event does not contain a valid issue number")

        issue_body = issue.get("body")
        if issue_body is None:
            issue_body = ""
        if not isinstance(issue_body, str):
            raise ValueError("GitHub event contains an invalid issue body")

        return cls(
            github_token=_required_env("GITHUB_TOKEN"),
            repository=repository,
            issue_number=issue_number,
            issue_body=issue_body,
            gemini_api_key=os.environ.get("GEMINI_API_KEY", "").strip(),
            gemini_model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
            or "gemini-3.5-flash",
        )


def _load_github_event() -> dict[str, Any]:
    event_path = _required_env("GITHUB_EVENT_PATH")
    try:
        data = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Failed to read GitHub event: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("GitHub event must be a JSON object")
    return data


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Required environment variable is missing: {name}")
    return value


def _required_nested_string(data: dict[str, Any], *keys: str) -> str:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            raise ValueError(f"GitHub event does not contain {'.'.join(keys)}")
        value = value.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"GitHub event does not contain {'.'.join(keys)}")
    return value.strip()
