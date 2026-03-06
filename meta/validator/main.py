"""Governance validator entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from meta.logger import get_app_logger
from meta.validator.contributors import ContributorValidator, load_contributors
from meta.validator.shared.reporter import Reporter
from meta.validator.teams import TeamValidator, load_teams


def main() -> None:
    """CLI entry point."""
    logger = get_app_logger()
    if not Path("contributors").exists():
        logger.critical("Please run this binary from the workspace root.")
        sys.exit(1)

    load_dotenv()

    reporter = Reporter()
    contributors = load_contributors(reporter)
    teams = load_teams(reporter)

    ContributorValidator(contributors, reporter).validate()
    TeamValidator(teams, contributors, reporter).validate()

    reporter.emit()
