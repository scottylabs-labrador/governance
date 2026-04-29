"""Mock client implementations for validator tests."""

from .mock_github_client import (
    MockGithubClientNotFound,
    MockGithubClientRateLimitExceeded,
    MockGithubClientUnexpectedError,
    MockGithubClientValid,
    make_get_github_client,
)
from .mock_keycloak_client import (
    MockKeycloakClientGithubUnexpectedError,
    MockKeycloakClientMismatchedGithub,
    MockKeycloakClientMissingGithub,
    MockKeycloakClientUnexpectedError,
    MockKeycloakClientUserNotFound,
    MockKeycloakClientValid,
    make_get_keycloak_client,
)

__all__ = [
    "MockGithubClientNotFound",
    "MockGithubClientRateLimitExceeded",
    "MockGithubClientUnexpectedError",
    "MockGithubClientValid",
    "MockKeycloakClientGithubUnexpectedError",
    "MockKeycloakClientMismatchedGithub",
    "MockKeycloakClientMissingGithub",
    "MockKeycloakClientUnexpectedError",
    "MockKeycloakClientUserNotFound",
    "MockKeycloakClientValid",
    "make_get_github_client",
    "make_get_keycloak_client",
]
