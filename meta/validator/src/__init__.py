"""Validator entry point."""

from __future__ import annotations

from dotenv import load_dotenv

from meta.loaders.members import load_members
from meta.loaders.teams import load_teams
from meta.logger import print_section

from .members import MemberValidator
from .reporter import Reporter, bind_reporter
from .teams import TeamValidator


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    reporter = Reporter()

    record = bind_reporter(reporter)
    print_section("Validating members")
    members = load_members(record)
    MemberValidator(members, reporter).validate()

    print_section("Validating teams")
    teams = load_teams(record)
    TeamValidator(teams, members, reporter).validate()

    reporter.emit()
