from __future__ import annotations

import ipaddress
import re
from urllib.parse import SplitResult, urlsplit


ALLOWED_HOSTS = {"qiita.com", "zenn.dev"}
URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}\"']+", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;:!?。、，；：！？"


def extract_first_url(text: str) -> str:
    match = URL_PATTERN.search(text)
    if not match:
        raise ValueError("Issue body does not contain an HTTP(S) URL")
    return match.group(0).rstrip(TRAILING_PUNCTUATION)


def validate_article_url(url: str) -> SplitResult:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid article URL") from exc

    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS article URLs are allowed")
    if parsed.username or parsed.password:
        raise ValueError("Credentials in article URLs are not allowed")
    if port not in (None, 443):
        raise ValueError("Non-standard ports are not allowed")

    hostname = (parsed.hostname or "").lower().rstrip(".")
    if hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Unsupported article host: {hostname or '(empty)'}")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("Private or local IP addresses are not allowed")

    if not parsed.path or parsed.path == "/":
        raise ValueError("Article URL does not contain an article path")
    return parsed._replace(netloc=hostname)
