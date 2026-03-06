"""Governance validator entry point."""

import asyncio
import logging
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .checks import (
    validate_cross_references,
    validate_file_names,
    validate_github_repositories,
    validate_github_users,
    validate_key_orderings,
    validate_maintainers_are_contributors,
    validate_slack_ids,
)
from .loader import load_contributors, load_schema_key_ordering, load_teams
from .model import (
    FileValidationMessages,
    ValidationError,
    ValidationReport,
    ValidationStatistics,
    ValidationWarning,
)


def _insert_error(
    files: dict[str, FileValidationMessages],
    error: ValidationError,
) -> None:
    if error.file not in files:
        files[error.file] = FileValidationMessages()
    files[error.file].errors.append(error)


def _insert_warning(
    files: dict[str, FileValidationMessages],
    warning: ValidationWarning,
) -> None:
    if warning.file not in files:
        files[warning.file] = FileValidationMessages()
    files[warning.file].warnings.append(warning)


def _blue(text: str) -> str:
    return f"\033[34m\033[1m{text}\033[0m"


def _red(text: str) -> str:
    return f"\033[31m\033[1m{text}\033[0m"


def _yellow(text: str) -> str:
    return f"\033[33m\033[1m{text}\033[0m"


def _green(text: str) -> str:
    return f"\033[32m\033[1m{text}\033[0m"


async def run() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    if not Path("contributors").exists():
        logger.error("Please run this binary from the workspace root.")
        sys.exit(1)

    contributors = load_contributors()
    teams = load_teams()
    contributor_ordering = load_schema_key_ordering(
        "__meta/schemas/contributor.schema.json"
    )
    team_ordering = load_schema_key_ordering("__meta/schemas/team.schema.json")

    file_messages: dict[str, FileValidationMessages] = {
        f"contributors/{k.name}.toml": FileValidationMessages()
        for k in contributors
    }
    for k in teams:
        file_messages[f"teams/{k.name}.toml"] = FileValidationMessages()

    for error in validate_key_orderings(contributors, contributor_ordering):
        _insert_error(file_messages, error)
    for error in validate_key_orderings(teams, team_ordering):
        _insert_error(file_messages, error)
    for error in validate_file_names(contributors, teams):
        _insert_error(file_messages, error)
    for error in validate_maintainers_are_contributors(teams):
        _insert_error(file_messages, error)
    for error in validate_cross_references(contributors, teams):
        _insert_error(file_messages, error)

    async with httpx.AsyncClient() as client:
        gh_errors, gh_warnings = await validate_github_users(contributors, client)
        for error in gh_errors:
            _insert_error(file_messages, error)
        for warning in gh_warnings:
            _insert_warning(file_messages, warning)

        gh_repo_errors, gh_repo_warnings = await validate_github_repositories(
            teams, client
        )
        for error in gh_repo_errors:
            _insert_error(file_messages, error)
        for warning in gh_repo_warnings:
            _insert_warning(file_messages, warning)

        slack_errors, slack_warnings = await validate_slack_ids(
            contributors, teams, client
        )
        for error in slack_errors:
            _insert_error(file_messages, error)
        for warning in slack_warnings:
            _insert_warning(file_messages, warning)

    total_errors = sum(len(m.errors) for m in file_messages.values())
    total_warnings = sum(len(m.warnings) for m in file_messages.values())
    valid_files = sum(1 for m in file_messages.values() if not m.errors)
    invalid_files = len(file_messages) - valid_files

    stats = ValidationStatistics(
        contributors_count=len(contributors),
        teams_count=len(teams),
        valid_files_count=valid_files,
        invalid_files_count=invalid_files,
        total_errors=total_errors,
        total_warnings=total_warnings,
    )
    report = ValidationReport(
        valid=(invalid_files == 0),
        stats=stats,
        files=file_messages,
    )

    print(_blue("===== SUMMARY ====="))
    print(f"Contributors: {report.stats.contributors_count}")
    print(f"Teams: {report.stats.teams_count}")
    print(f"Valid files: {report.stats.valid_files_count}")
    print(f"Invalid files: {report.stats.invalid_files_count}")
    print(f"Total errors: {report.stats.total_errors}")
    print(f"Total warnings: {report.stats.total_warnings}")

    if report.stats.total_errors > 0:
        print()
        print(_red("===== ERRORS ====="))
        for file_path, messages in report.files.items():
            if not messages.errors:
                continue
            print(file_path)
            for err in messages.errors:
                print(f"  - {err.message}")

    if report.stats.total_warnings > 0:
        print()
        print(_yellow("===== WARNINGS ====="))
        for file_path, messages in report.files.items():
            if not messages.warnings:
                continue
            print(file_path)
            for warn in messages.warnings:
                print(f"  - {warn.message}")

    if not report.valid:
        print()
        print(
            f"Validation failed with {_red(str(report.stats.total_errors))} "
            f"error(s) in {_red(str(report.stats.invalid_files_count))} file(s)"
        )
        sys.exit(1)

    print()
    print(_green("Validation passed!"))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
