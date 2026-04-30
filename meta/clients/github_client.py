"""GitHub client."""

import os
from http import HTTPStatus
from typing import TYPE_CHECKING

from github import Auth, Github, GithubException

from meta.logger import get_app_logger

if TYPE_CHECKING:
    from github.Repository import Repository


def get_github_client() -> Github:
    """Get the Github client."""
    logger = get_app_logger()

    github_token = os.getenv("SYNC_GITHUB_TOKEN")
    if not github_token:
        msg = "SYNC_GITHUB_TOKEN is not set"
        logger.critical(msg)
        raise RuntimeError(msg)

    return Github(auth=Auth.Token(github_token))


def get_github_file(
    repo: Repository,
    file_path: str,
) -> tuple[str | None, str | None]:
    """Get the current file from the repository.

    Returns:
        tuple[str | None, str | None]: The current file content
        and the sha of the file. The sha is None if the file does not exist.

    """
    try:
        contents = repo.get_contents(file_path)
    except GithubException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            return None, None
        raise

    if isinstance(contents, list):
        return None, None

    sha = contents.sha
    current_content = contents.decoded_content.decode("utf-8")
    return current_content, sha
