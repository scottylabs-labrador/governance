"""Test the team validator."""

from __future__ import annotations

from meta.validator.src.members.loader import load_members
from meta.validator.src.reporter import ErrorCode, Reporter
from meta.validator.src.teams.loader import load_teams
from meta.validator.src.teams.validator import TeamValidator
from meta.validator.tests.helper import has_error, no_errors

MEMBERS_FOR_TEAMS = "meta/validator/tests/members/for_teams/*.toml"


def test_team_valid() -> None:
    """A well-formed team and matching members produce no errors."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/valid.toml")
    assert no_errors(reporter)
    TeamValidator(teams, members, reporter).validate_sync()
    assert no_errors(reporter)


def test_team_wrong_key_ordering() -> None:
    """Top-level TOML keys must follow ``team.schema.json`` property order."""
    reporter = Reporter()
    load_teams(reporter, "meta/validator/tests/teams/wrong-key-ordering.toml")
    assert has_error(reporter, ErrorCode.TEAM_KEY_ORDERING)


def test_team_unknown_member_cross_reference() -> None:
    """Every team member github username must exist in the members index."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/unknown-member.toml")
    assert no_errors(reporter)
    TeamValidator(teams, members, reporter).validate()
    assert has_error(reporter, ErrorCode.MEMBER_CROSS_REFERENCE)


def test_team_lead_not_in_members() -> None:
    """Every lead must also appear under membership members."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/lead-not-member.toml")
    assert no_errors(reporter)
    TeamValidator(teams, members, reporter).validate()
    assert has_error(reporter, ErrorCode.LEAD_CROSS_REFERENCE)


def test_team_not_file() -> None:
    """Teams must be a file."""
    reporter = Reporter()
    load_teams(reporter, "meta/validator/tests/teams/*")
    assert has_error(reporter, ErrorCode.TEAM_NOT_FILE)
