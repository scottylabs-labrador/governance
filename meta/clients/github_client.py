"""GitHub client."""

import os

from github import Auth, Github

from meta.logger import get_app_logger


def get_github_client() -> Github:
    """Get the Github client."""
    logger = get_app_logger()

    github_token = os.getenv("SYNC_GITHUB_TOKEN")
    if not github_token:
        msg = "SYNC_GITHUB_TOKEN is not set"
        logger.critical(msg)
        raise RuntimeError(msg)

    return Github(auth=Auth.Token(github_token))
