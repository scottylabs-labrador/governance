"""GitHub client."""

import os
from functools import lru_cache

from github import Auth, Github

from meta.logger import get_app_logger


@lru_cache(maxsize=1)
def get_github_client() -> Github:
    """Get the Github client. Cache the result for reuse across the app."""
    logger = get_app_logger()

    github_token = os.getenv("SYNC_GITHUB_TOKEN")
    if not github_token:
        msg = "SYNC_GITHUB_TOKEN is not set"
        logger.critical(msg)
        raise RuntimeError(msg)

    return Github(auth=Auth.Token(github_token))
