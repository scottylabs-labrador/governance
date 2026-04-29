"""Member validation runner."""

from __future__ import annotations

import asyncio
import sys
from http import HTTPStatus
from typing import TYPE_CHECKING

import httpx
from github import GithubException

from meta.clients.github_client import get_github_client
from meta.clients.keycloak_client import get_keycloak_client
from meta.logger import get_app_logger
from meta.validator.src.reporter import ErrorCode

if TYPE_CHECKING:
    from meta.models import Member
    from meta.validator.src.reporter import Reporter


class MemberValidationError(Exception):
    """Raised when validation fails for a single member."""


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
        """Validate all members in parallel."""
        try:
            asyncio.run(self._validate_async())
        except MemberValidationError:
            sys.exit(1)

    async def _validate_async(self) -> None:
        """Validate each member concurrently using a shared async HTTP client scope."""
        async with httpx.AsyncClient() as _:
            await asyncio.gather(
                *[
                    self._validate_member(github_username, member)
                    for github_username, member in self.members.items()
                ],
            )

    async def _validate_member(
        self,
        github_username: str,
        member: Member,
    ) -> None:
        """Run validation for a single member."""
        await asyncio.to_thread(self.validate_github, github_username)
        await asyncio.to_thread(self.validate_keycloak, github_username, member)

    def validate_github(self, github_username: str) -> None:
        """Validate that the GitHub username is valid with GitHub API."""
        github_client = get_github_client()
        try:
            github_client.get_user(github_username)
        except GithubException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                self.reporter.insert_error(
                    github_username,
                    ErrorCode.INVALID_GITHUB_USERNAME,
                    f"GitHub user {github_username} not found",
                )
                return

            self.logger.exception(
                "Error validating GitHub username: %s",
                github_username,
            )
            raise MemberValidationError from e
        except Exception as e:
            self.logger.exception(
                "Error validating GitHub username: %s",
                github_username,
            )
            raise MemberValidationError from e

    def validate_keycloak(self, github_username: str, member: Member) -> None:
        """Validate that the Andrew ID maps to a user in Keycloak."""
        keycloak_client = get_keycloak_client()
        andrew_id = member.andrew_id
        if andrew_id is None:
            return

        try:
            user = keycloak_client.get_user_id_by_username(andrew_id)
            if user is None:
                self.reporter.insert_error(
                    member.file_path,
                    ErrorCode.INVALID_KEYCLOAK_USERNAME,
                    f"User {andrew_id} not found in Keycloak",
                )
                return

            keycloak_github_username = keycloak_client.get_user_github_username(
                user,
            )
            if keycloak_github_username is None:
                self.reporter.insert_error(
                    member.file_path,
                    ErrorCode.MISSING_KEYCLOAK_GITHUB,
                    f"User {andrew_id} is not linked to a GitHub account in Keycloak",
                )
                return

            if github_username.lower() != keycloak_github_username.lower():
                self.reporter.insert_error(
                    member.file_path,
                    ErrorCode.MISMATCHED_KEYCLOAK_GITHUB,
                    f"User {andrew_id} linked to a different GitHub account in "
                    f"Keycloak: {keycloak_github_username} != {github_username}",
                )
                return

            slack_id = keycloak_client.get_user_slack_id(user)
            if slack_id is None:
                self.reporter.insert_error(
                    member.file_path,
                    ErrorCode.MISSING_KEYCLOAK_SLACK,
                    f"User {andrew_id} is not linked to a Slack account in Keycloak",
                )
                return

        except Exception as e:
            self.logger.exception(
                "Error validating Keycloak: %s",
                andrew_id,
            )
            raise MemberValidationError from e
