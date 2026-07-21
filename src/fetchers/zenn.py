from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit

import requests
from bs4 import BeautifulSoup

from src.fetchers.base import Article, BaseFetcher
from src.utils.url import validate_article_url


class ZennFetcher(BaseFetcher):
    MAX_RESPONSE_BYTES = 5 * 1024 * 1024
    ARTICLE_PATH = re.compile(r"^/[^/]+/articles/[^/]+(?:/)?$")

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def fetch(self, url: str) -> Article:
        if not self.ARTICLE_PATH.fullmatch(unquote(urlsplit(url).path)):
            raise ValueError("Unsupported Zenn article URL")

        response = requests.get(
            url,
            headers={"Accept": "text/html", "User-Agent": "tech-article-digest"},
            timeout=self.timeout,
            allow_redirects=True,
            stream=True,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Zenn request failed ({response.status_code})"
            ) from exc

        final_url = validate_article_url(response.url)
        if not self.ARTICLE_PATH.fullmatch(unquote(final_url.path)):
            raise RuntimeError("Zenn redirected outside an article URL")
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" not in content_type:
            raise RuntimeError("Zenn response is not HTML")

        chunks: list[bytes] = []
        size = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            size += len(chunk)
            if size > self.MAX_RESPONSE_BYTES:
                raise RuntimeError("Zenn response is too large")
            chunks.append(chunk)
        html = b"".join(chunks)
        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_title(soup)
        article = soup.select_one("article") or soup.select_one(".znc")
        if article is None:
            raise RuntimeError("Could not find the Zenn article body")
        for element in article.select("script, style, noscript, svg"):
            element.decompose()
        body = article.get_text("\n", strip=True)
        if not title or not body:
            raise RuntimeError("Zenn article is empty")
        return Article(title=title, body=body, url=response.url)

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        meta = soup.select_one('meta[property="og:title"]')
        if meta and meta.get("content"):
            return str(meta["content"]).strip()
        heading = soup.select_one("h1")
        return heading.get_text(" ", strip=True) if heading else ""
