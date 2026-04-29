"""Test the team validator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from meta.validator.src.members.loader import load_members
from meta.validator.src.reporter import ErrorCode, Reporter
from meta.validator.src.teams import validator as teams_validator
from meta.validator.src.teams.loader import load_teams
from meta.validator.src.teams.validator import TeamValidator
from meta.validator.tests.helper import has_error, no_errors
from meta.validator.tests.mock_clients.mock_github_client import (
    MockGithubClientNotFound,
    MockGithubClientRateLimitExceeded,
    MockGithubClientValid,
    make_get_github_client,
)

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

MEMBERS_FOR_TEAMS = "meta/validator/tests/members/for_teams/*.toml"


def test_team_valid(monkeypatch: MonkeyPatch) -> None:
    """A well-formed team and matching members produce no errors."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/valid.toml")
    assert no_errors(reporter)
    monkeypatch.setattr(
        teams_validator,
        "get_github_client",
        make_get_github_client(MockGithubClientValid()),
    )
    TeamValidator(teams, members, reporter).validate()
    assert no_errors(reporter)


def test_team_wrong_key_ordering() -> None:
    """Top-level TOML keys must follow ``team.schema.json`` property order."""
    reporter = Reporter()
    load_teams(reporter, "meta/validator/tests/teams/wrong-key-ordering.toml")
    assert has_error(reporter, ErrorCode.TEAM_KEY_ORDERING)


def test_team_unknown_member_cross_reference(monkeypatch: MonkeyPatch) -> None:
    """Every team member github username must exist in the members index."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/unknown-member.toml")
    assert no_errors(reporter)
    monkeypatch.setattr(
        teams_validator,
        "get_github_client",
        make_get_github_client(MockGithubClientValid()),
    )
    TeamValidator(teams, members, reporter).validate()
    assert has_error(reporter, ErrorCode.MEMBER_CROSS_REFERENCE)


def test_team_lead_not_in_members(monkeypatch: MonkeyPatch) -> None:
    """Every lead must also appear under membership members."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/lead-not-member.toml")
    assert no_errors(reporter)
    monkeypatch.setattr(
        teams_validator,
        "get_github_client",
        make_get_github_client(MockGithubClientValid()),
    )
    TeamValidator(teams, members, reporter).validate()
    assert has_error(reporter, ErrorCode.LEAD_CROSS_REFERENCE)


def test_rate_limited_github_team_repo_exits(monkeypatch: MonkeyPatch) -> None:
    """Non-404 ``GithubException`` during repo checks should abort validation."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/valid.toml")
    assert no_errors(reporter)
    monkeypatch.setattr(
        teams_validator,
        "get_github_client",
        make_get_github_client(MockGithubClientRateLimitExceeded()),
    )
    with pytest.raises(SystemExit, match="1"):
        TeamValidator(teams, members, reporter).validate()


def test_team_github_repo_not_found(monkeypatch: MonkeyPatch) -> None:
    """A missing GitHub repo should be reported as ``GITHUB_REPO_NOT_FOUND``."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/valid.toml")
    assert no_errors(reporter)
    monkeypatch.setattr(
        teams_validator,
        "get_github_client",
        make_get_github_client(MockGithubClientNotFound()),
    )
    TeamValidator(teams, members, reporter).validate()
    assert has_error(reporter, ErrorCode.GITHUB_REPO_NOT_FOUND)


def test_team_not_file() -> None:
    """Teams must be a file."""
    reporter = Reporter()
    load_teams(reporter, "meta/validator/tests/teams/*")
    assert has_error(reporter, ErrorCode.TEAM_NOT_FILE)
