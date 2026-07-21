from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    title: str
    body: str
    url: str


class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, url: str) -> Article:
        """Fetch an article from a validated URL."""
