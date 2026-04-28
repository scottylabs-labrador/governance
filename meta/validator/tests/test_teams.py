"""Tests for team loading and ``TeamValidator``."""

from __future__ import annotations

from meta.validator.src.members.loader import load_members
from meta.validator.src.reporter import Reporter
from meta.validator.src.teams.loader import load_teams
from meta.validator.src.teams.validator import TeamValidator

MEMBERS_FOR_TEAMS = "meta/validator/tests/members/for_teams/*.toml"


def _flatten_errors(reporter: Reporter) -> list[str]:
    return [msg for msgs in reporter._errors.values() for msg in msgs]  # noqa: SLF001


def test_team_valid() -> None:
    """A well-formed team and matching members produce no errors."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/valid.toml")
    assert not reporter._errors  # noqa: SLF001
    TeamValidator(teams, members, reporter).validate_sync()
    assert not reporter._errors  # noqa: SLF001


def test_team_wrong_key_ordering() -> None:
    """Top-level TOML keys must follow ``team.schema.json`` property order."""
    reporter = Reporter()
    load_teams(reporter, "meta/validator/tests/teams/wrong-key-ordering.toml")
    messages = _flatten_errors(reporter)
    assert messages
    assert any("Invalid key order" in m for m in messages)


def test_team_unknown_member_cross_reference() -> None:
    """Every team member github username must exist in the members index."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/unknown-member.toml")
    assert not reporter._errors  # noqa: SLF001
    TeamValidator(teams, members, reporter).validate()
    messages = _flatten_errors(reporter)
    assert any("Unknown member: charlie" in m for m in messages)


def test_team_lead_not_in_members() -> None:
    """Every lead must also appear under membership members."""
    reporter = Reporter()
    members = load_members(reporter, MEMBERS_FOR_TEAMS)
    teams = load_teams(reporter, "meta/validator/tests/teams/lead-not-member.toml")
    assert not reporter._errors  # noqa: SLF001
    TeamValidator(teams, members, reporter).validate()
    messages = _flatten_errors(reporter)
    assert any("Lead 'alice' missing from members" in m for m in messages)


def test_team_not_file() -> None:
    """Teams must be a file."""
    reporter = Reporter()
    load_teams(reporter, "meta/validator/tests/teams/*")
    assert len(reporter._errors) > 0  # noqa: SLF001
