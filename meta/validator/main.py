"""Governance validator entry point."""

from __future__ import annotations

from dotenv import load_dotenv

from meta.validator.members import MemberValidator, load_members
from meta.validator.shared.reporter import Reporter
from meta.validator.teams import TeamValidator, load_teams


def main() -> None:
    """CLI entry point."""
    load_dotenv()

    reporter = Reporter()
    members = load_members(reporter)
    teams = load_teams(reporter)

    MemberValidator(members, reporter).validate()
    TeamValidator(teams, members, reporter).validate()

    reporter.emit()
