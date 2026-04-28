"""Mock GitHub clients for validator tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github import GithubException

if TYPE_CHECKING:
    from collections.abc import Callable


class MockGithubClientValid:
    """Mock GitHub client that treats all users as valid."""

    def get_user(self, _github_username: str) -> None:
        """Pretend the looked up GitHub user exists."""
        return


class MockGithubClientRecorder:
    """Mock GitHub client collecting requested usernames."""

    def __init__(self) -> None:
        """Initialize the request recorder."""
        self.requested_usernames: list[str] = []

    def get_user(self, github_username: str) -> None:
        """Record the looked up GitHub username."""
        self.requested_usernames.append(github_username)


class MockGithubClientNotFound:
    """Mock GitHub client that always raises not-found."""

    def get_user(self, _github_username: str) -> None:
        """Raise a not-found response to emulate invalid users."""
        raise GithubException(status=404, data={"message": "Not Found"})


type MockGithubClient = (
    MockGithubClientValid | MockGithubClientRecorder | MockGithubClientNotFound
)


def make_get_github_client(
    client: MockGithubClient,
) -> Callable[[], MockGithubClient]:
    """Return a ``get_github_client``-compatible callable for monkeypatching."""

    def mock_get_github_client() -> MockGithubClient:
        """Return the provided mock client."""
        return client

    return mock_get_github_client
