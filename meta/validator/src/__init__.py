"""Governance validator entry point."""

from __future__ import annotations

from dotenv import load_dotenv

from meta.loaders.members import load_members
from meta.loaders.teams import load_teams
from meta.logger import print_section
from meta.reporter import Reporter

from .members import MemberValidator
from .teams import TeamValidator


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    reporter = Reporter()

    print_section("Validating members")
    members = load_members(reporter)
    MemberValidator(members, reporter).validate()

    print_section("Validating teams")
    teams = load_teams(reporter)
    TeamValidator(teams, members, reporter).validate()

    reporter.emit()
