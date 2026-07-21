from __future__ import annotations

import logging

from src.ai.gemini import GeminiClient
from src.config import Settings
from src.fetchers.qiita import QiitaFetcher
from src.fetchers.zenn import ZennFetcher
from src.github.client import GitHubClient
from src.services.issue_service import IssueService
from src.services.summarizer import Summarizer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings.from_environment()
    github = GitHubClient(settings.github_token, settings.repository)
    service = IssueService(
        github=github,
        issue_number=settings.issue_number,
        summarizer=Summarizer(
            GeminiClient(settings.gemini_api_key, settings.gemini_model)
        ),
        fetchers={
            "qiita.com": QiitaFetcher(),
            "zenn.dev": ZennFetcher(),
        },
    )

    try:
        processed = service.process(settings.issue_body)
        if processed:
            logger.info("Issue #%s was summarized successfully", settings.issue_number)
        else:
            logger.info("Issue #%s is no longer pending; skipping", settings.issue_number)
    except Exception:
        logger.exception("Failed to summarize issue #%s", settings.issue_number)
        try:
            service.mark_failed()
        except Exception:
            logger.exception("Failed to apply the failed label")
        raise


if __name__ == "__main__":
    main()
