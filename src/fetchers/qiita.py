from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit

import requests

from src.fetchers.base import Article, BaseFetcher


class QiitaFetcher(BaseFetcher):
    API_BASE = "https://qiita.com/api/v2/items"
    ITEM_PATH = re.compile(r"^/[^/]+/items/([0-9a-f]+)(?:/)?$")

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def fetch(self, url: str) -> Article:
        match = self.ITEM_PATH.fullmatch(unquote(urlsplit(url).path))
        if not match:
            raise ValueError("Unsupported Qiita article URL")

        response = requests.get(
            f"{self.API_BASE}/{match.group(1)}",
            headers={"Accept": "application/json", "User-Agent": "tech-article-digest"},
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Qiita API request failed ({response.status_code})"
            ) from exc

        try:
            data = response.json()
            title = data["title"].strip()
            body = data["body"].strip()
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("Qiita API returned an invalid article") from exc
        if not title or not body:
            raise RuntimeError("Qiita article is empty")
        return Article(title=title, body=body, url=url)
