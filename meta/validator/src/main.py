"""Governance validator entry point."""

from __future__ import annotations

from dotenv import load_dotenv

from .members import MemberValidator, load_members
from .reporter import Reporter
from .teams import TeamValidator, load_teams


def main() -> None:
    """CLI entry point."""
    load_dotenv()

    reporter = Reporter()
    members = load_members(reporter)
    teams = load_teams(reporter)

    MemberValidator(members, reporter).validate()
    TeamValidator(teams, members, reporter).validate()

    reporter.emit()
