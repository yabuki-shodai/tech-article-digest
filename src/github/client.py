from __future__ import annotations

import requests


class GitHubClient:
    API_BASE = "https://api.github.com"
    LABEL_COLORS = {
        "completed": "0e8a16",
        "failed": "d73a4a",
    }

    def __init__(self, token: str, repository: str, timeout: int = 20) -> None:
        if "/" not in repository:
            raise ValueError("Invalid GitHub repository name")
        self.repository = repository
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "tech-article-digest",
            }
        )

    def add_comment(self, issue_number: int, body: str) -> None:
        self._request(
            "POST",
            f"/repos/{self.repository}/issues/{issue_number}/comments",
            json={"body": body},
        )

    def replace_processing_label(self, issue_number: int, target: str) -> None:
        self._ensure_label(target)
        issue = self._request(
            "GET", f"/repos/{self.repository}/issues/{issue_number}"
        ).json()
        labels = [
            label["name"]
            for label in issue.get("labels", [])
            if isinstance(label, dict)
            and label.get("name") not in {"summarize", "completed", "failed"}
        ]
        labels.append(target)
        self._request(
            "PATCH",
            f"/repos/{self.repository}/issues/{issue_number}",
            json={"labels": labels},
        )

    def close_issue(self, issue_number: int) -> None:
        self._request(
            "PATCH",
            f"/repos/{self.repository}/issues/{issue_number}",
            json={"state": "closed", "state_reason": "completed"},
        )

    def _ensure_label(self, name: str) -> None:
        response = self.session.get(
            f"{self.API_BASE}/repos/{self.repository}/labels/{name}",
            timeout=self.timeout,
        )
        if response.status_code == 404:
            self._request(
                "POST",
                f"/repos/{self.repository}/labels",
                json={
                    "name": name,
                    "color": self.LABEL_COLORS[name],
                    "description": f"Article summarization {name}",
                },
            )
            return
        self._raise_for_status(response)

    def _request(self, method: str, path: str, **kwargs: object) -> requests.Response:
        response = self.session.request(
            method,
            f"{self.API_BASE}{path}",
            timeout=self.timeout,
            **kwargs,
        )
        self._raise_for_status(response)
        return response

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = response.text[:1000]
            raise RuntimeError(
                f"GitHub API request failed ({response.status_code}): {detail}"
            ) from exc
