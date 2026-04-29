"""Mock client implementations for validator tests."""

from .mock_github_client import (
    MockGithubClientNotFound,
    MockGithubClientRateLimitExceeded,
    MockGithubClientValid,
    make_get_github_client,
)
from .mock_keycloak_client import (
    MockKeycloakClientGithubUnexpectedError,
    MockKeycloakClientMismatchedGithub,
    MockKeycloakClientMissingGithub,
    MockKeycloakClientMissingSlack,
    MockKeycloakClientSlackUnexpectedError,
    MockKeycloakClientUnexpectedError,
    MockKeycloakClientUserNotFound,
    MockKeycloakClientValid,
    make_get_keycloak_client,
)

__all__ = [
    "MockGithubClientNotFound",
    "MockGithubClientRateLimitExceeded",
    "MockGithubClientValid",
    "MockKeycloakClientGithubUnexpectedError",
    "MockKeycloakClientMismatchedGithub",
    "MockKeycloakClientMissingGithub",
    "MockKeycloakClientMissingSlack",
    "MockKeycloakClientSlackUnexpectedError",
    "MockKeycloakClientUnexpectedError",
    "MockKeycloakClientUserNotFound",
    "MockKeycloakClientValid",
    "make_get_github_client",
    "make_get_keycloak_client",
]
