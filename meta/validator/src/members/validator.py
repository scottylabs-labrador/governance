"""Member validation runner."""

from __future__ import annotations

import sys
from http import HTTPStatus
from typing import TYPE_CHECKING

from github import GithubException

from meta.clients.github_client import get_github_client
from meta.logger import get_app_logger
from meta.validator.src.reporter import ErrorCode

if TYPE_CHECKING:
    from meta.models import Member
    from meta.validator.src.reporter import Reporter


class MemberValidator:
    """Run contributor validation and record results."""

    def __init__(
        self,
        members: dict[str, Member],
        reporter: Reporter,
    ) -> None:
        """Create a contributor validator."""
        self.members = members
        self.reporter = reporter
        self.logger = get_app_logger()

    def validate(self) -> None:
        """Validate all contributors.

        This includes:
        - Validating that the GitHub username is valid
        - Validating that the Andrew ID maps to a user in Keycloak
        - Validating that the email from Andrew ID is in Slack
        """
        self.validate_github_username()

    def validate_github_username(self) -> None:
        """Validate that the GitHub username is valid with GitHub API."""
        github_client = get_github_client()
        for github_username in self.members:
            try:
                github_client.get_user(github_username)
            except GithubException as e:
                if e.status == HTTPStatus.NOT_FOUND:
                    self.reporter.insert_error(
                        github_username,
                        ErrorCode.INVALID_GITHUB_USERNAME,
                        f"GitHub user {github_username} not found",
                    )
            except Exception:
                # If there is an error validating the GitHub username, we don't
                # want to spam GitHub API with more requests, so we exit the program.
                self.logger.exception(
                    "Error validating GitHub username: %s",
                    github_username,
                )
                sys.exit(1)
