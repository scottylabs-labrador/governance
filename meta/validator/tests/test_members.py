"""Test the member validator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from meta.validator.src.members import validator as members_validator
from meta.validator.src.members.loader import load_members
from meta.validator.src.members.validator import MemberValidator
from meta.validator.src.reporter import ErrorCode, Reporter
from meta.validator.tests.helper import has_error, no_errors
from meta.validator.tests.mock_clients.mock_github_client import (
    MockGithubClientNotFound,
    MockGithubClientRateLimitExceeded,
    MockGithubClientValid,
    make_get_github_client,
)
from meta.validator.tests.mock_clients.mock_keycloak_client import (
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

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_member_valid(monkeypatch: MonkeyPatch) -> None:
    """Members must be valid."""
    reporter = Reporter()
    members = load_members(reporter, "meta/validator/tests/members/valid.toml")
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientValid()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )
    MemberValidator(members, reporter).validate()
    assert no_errors(reporter)


def test_member_github_username_match_is_case_insensitive(
    monkeypatch: MonkeyPatch,
) -> None:
    """Keycloak GitHub login may differ in case from the members file stem."""
    reporter = Reporter()
    members = load_members(reporter, "meta/validator/tests/members/valid.toml")
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientValid(
        github_username_by_andrew_id={"valid": "VaLiD"},
    )
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )
    MemberValidator(members, reporter).validate()
    assert no_errors(reporter)


def test_member_key_ordering() -> None:
    """Members key ordering must be validated."""
    reporter = Reporter()
    load_members(reporter, "meta/validator/tests/members/wrong-key-ordering.toml")
    assert has_error(reporter, ErrorCode.MEMBER_KEY_ORDERING)


def test_member_not_file() -> None:
    """Members must be a file."""
    reporter = Reporter()
    load_members(reporter, "meta/validator/tests/members/*")
    assert has_error(reporter, ErrorCode.MEMBER_NOT_FILE)


def test_not_found_github_username(
    monkeypatch: MonkeyPatch,
) -> None:
    """A GitHub 404 should be reported as ``INVALID_GITHUB_USERNAME``."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientNotFound()
    mock_keycloak = MockKeycloakClientValid()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    MemberValidator(members, reporter).validate()

    assert has_error(reporter, ErrorCode.INVALID_GITHUB_USERNAME)


def test_rate_limited_github_username(
    monkeypatch: MonkeyPatch,
) -> None:
    """A GitHub rate-limit response should abort validation early."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientRateLimitExceeded()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )

    with pytest.raises(SystemExit, match="1"):
        MemberValidator(members, reporter).validate()


def test_not_found_keycloak_username(monkeypatch: MonkeyPatch) -> None:
    """A missing Keycloak user should be reported as ``INVALID_KEYCLOAK_USERNAME``."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientUserNotFound()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    MemberValidator(members, reporter).validate()

    assert has_error(reporter, ErrorCode.INVALID_KEYCLOAK_USERNAME)


def test_missing_keycloak_github(monkeypatch: MonkeyPatch) -> None:
    """A Keycloak user without GitHub federation is an error."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientMissingGithub()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    MemberValidator(members, reporter).validate()

    assert has_error(reporter, ErrorCode.MISSING_KEYCLOAK_GITHUB)


def test_mismatched_keycloak_github(monkeypatch: MonkeyPatch) -> None:
    """Keycloak GitHub login must match the member file stem."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientMismatchedGithub()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    MemberValidator(members, reporter).validate()

    assert has_error(reporter, ErrorCode.MISMATCHED_KEYCLOAK_GITHUB)


def test_unexpected_keycloak_client_error_exits(
    monkeypatch: MonkeyPatch,
) -> None:
    """Unexpected Keycloak errors should hit generic ``except Exception`` and exit."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientUnexpectedError()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    with pytest.raises(SystemExit, match="1"):
        MemberValidator(members, reporter).validate()


def test_unexpected_keycloak_github_link_error_exits(
    monkeypatch: MonkeyPatch,
) -> None:
    """Errors while reading GitHub from Keycloak should abort validation."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientGithubUnexpectedError()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    with pytest.raises(SystemExit, match="1"):
        MemberValidator(members, reporter).validate()


def test_missing_keycloak_slack(monkeypatch: MonkeyPatch) -> None:
    """A Keycloak user without Slack federation is an error."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientMissingSlack()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    MemberValidator(members, reporter).validate()

    assert has_error(reporter, ErrorCode.MISSING_KEYCLOAK_SLACK)


def test_unexpected_keycloak_slack_link_error_exits(
    monkeypatch: MonkeyPatch,
) -> None:
    """Errors while reading Slack from Keycloak should abort validation."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientSlackUnexpectedError()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    with pytest.raises(SystemExit, match="1"):
        MemberValidator(members, reporter).validate()


def test_skips_keycloak_when_no_andrew_id(monkeypatch: MonkeyPatch) -> None:
    """Members without ``andrew-id`` should not trigger Keycloak username checks."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/no-andrew-id.toml",
    )
    assert no_errors(reporter)

    mock_github = MockGithubClientValid()
    mock_keycloak = MockKeycloakClientUnexpectedError()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_github),
    )
    monkeypatch.setattr(
        members_validator,
        "get_keycloak_client",
        make_get_keycloak_client(mock_keycloak),
    )

    MemberValidator(members, reporter).validate()
    assert no_errors(reporter)
