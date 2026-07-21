from __future__ import annotations

from src.fetchers.base import BaseFetcher
from src.github.client import GitHubClient
from src.services.summarizer import Summarizer
from src.utils.url import extract_first_url, validate_article_url


class IssueService:
    def __init__(
        self,
        github: GitHubClient,
        issue_number: int,
        summarizer: Summarizer,
        fetchers: dict[str, BaseFetcher],
    ) -> None:
        self.github = github
        self.issue_number = issue_number
        self.summarizer = summarizer
        self.fetchers = fetchers

    def process(self, issue_body: str) -> bool:
        if not self.github.claim_issue(self.issue_number):
            return False

        url = extract_first_url(issue_body)
        parsed = validate_article_url(url)
        fetcher = self.fetchers.get(parsed.hostname or "")
        if fetcher is None:
            raise ValueError(f"Unsupported article host: {parsed.hostname}")

        article = fetcher.fetch(url)
        self.github.update_issue_title(self.issue_number, article.title)
        summary = self.summarizer.summarize(article)
        self.github.add_comment(self.issue_number, summary)
        self.github.replace_processing_label(self.issue_number, "completed")
        self.github.close_issue(self.issue_number)
        return True

    def mark_failed(self) -> None:
        self.github.replace_processing_label(self.issue_number, "failed")
