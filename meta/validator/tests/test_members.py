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
    MockGithubClientUnexpectedError,
    MockGithubClientValid,
    make_get_github_client,
)

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

def test_member_valid(monkeypatch: MonkeyPatch) -> None:
    """Members must be valid."""
    mock_client = MockGithubClientValid()

    reporter = Reporter()
    members = load_members(reporter, "meta/validator/tests/members/valid.toml")
    assert no_errors(reporter)
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_client),
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

    mock_client = MockGithubClientNotFound()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_client),
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

    mock_client = MockGithubClientRateLimitExceeded()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_client),
    )

    with pytest.raises(SystemExit, match="1"):
        MemberValidator(members, reporter).validate()


def test_unexpected_github_client_error_exits(
    monkeypatch: MonkeyPatch,
) -> None:
    """Unexpected client errors should hit generic ``except Exception`` and exit."""
    reporter = Reporter()
    members = load_members(
        reporter,
        "meta/validator/tests/members/for_teams/alice.toml",
    )
    assert no_errors(reporter)

    mock_client = MockGithubClientUnexpectedError()
    monkeypatch.setattr(
        members_validator,
        "get_github_client",
        make_get_github_client(mock_client),
    )

    with pytest.raises(SystemExit, match="1"):
        MemberValidator(members, reporter).validate()
