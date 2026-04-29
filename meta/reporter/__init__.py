"""Accumulate validation results and emit reports via logging."""

from __future__ import annotations

from collections import defaultdict
from enum import Enum

from meta.logger import get_app_logger


class ErrorCode(Enum):
    """Validation error types."""

    MEMBER_NOT_FILE = "Member not a file"
    TEAM_NOT_FILE = "Team not a file"
    MEMBER_KEY_ORDERING = "Member key ordering is invalid"
    TEAM_KEY_ORDERING = "Team key ordering is invalid"
    LEAD_CROSS_REFERENCE = "Lead missing from members in a team"
    MEMBER_CROSS_REFERENCE = "A member in team missing from members/"
    INVALID_GITHUB_USERNAME = "Invalid GitHub username"
    INVALID_KEYCLOAK_USERNAME = "Invalid Keycloak username"
    MISSING_KEYCLOAK_GITHUB = "Missing GitHub username in Keycloak"
    MISMATCHED_KEYCLOAK_GITHUB = "Mismatched GitHub username in Keycloak"
    MISSING_KEYCLOAK_SLACK = "Missing Slack ID in Keycloak"
    GITHUB_REPO_NOT_FOUND = "GitHub repository not found"


class Reporter:
    """Collects validation errors and emits a report."""

    def __init__(
        self,
    ) -> None:
        """Initialize file buckets for members and teams."""
        self.logger = get_app_logger()
        self._errors: defaultdict[str, list[tuple[ErrorCode, str]]] = defaultdict(
            list,
        )

    def insert_error(self, file_path: str, error: ErrorCode, message: str) -> None:
        """Insert a validation error into the per-file bucket."""
        self._errors[file_path].append((error, message))

    def emit(self) -> None:
        """Log the report and return whether the run is valid."""
        invalid_files = len(self._errors)
        total_errors = sum(len(errors) for errors in self._errors.values())

        self.logger.info("===== SUMMARY =====")
        self.logger.info("Invalid files: %s", invalid_files)
        self.logger.info("Total errors: %s", total_errors)

        if total_errors > 0:
            self.logger.error("===== ERRORS =====")
            for file_path, errors in self._errors.items():
                if not errors:
                    continue
                self.logger.error(file_path)
                for error in errors:
                    self.logger.error("  - %s", error[1])

            self.logger.critical(
                "Validation failed with %s error(s) in %s file(s)",
                total_errors,
                invalid_files,
            )
            raise SystemExit(1)

        self.logger.success("Validation passed!")
