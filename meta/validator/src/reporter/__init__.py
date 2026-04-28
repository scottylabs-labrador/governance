"""Accumulate validation results and emit reports via logging."""

from __future__ import annotations

from collections import defaultdict

from meta.logger import get_app_logger


class Reporter:
    """Collects validation errors and emits a report."""

    def __init__(
        self,
    ) -> None:
        """Initialize file buckets for members and teams."""
        self.logger = get_app_logger()
        self._errors: defaultdict[str, list[str]] = defaultdict(
            list,
        )

    def insert_error(self, file_path: str, message: str) -> None:
        """Insert a validation error into the per-file bucket."""
        self._errors[file_path].append(message)

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
                    self.logger.error("  - %s", error)

            self.logger.critical(
                "Validation failed with %s error(s) in %s file(s)",
                total_errors,
                invalid_files,
            )
            raise SystemExit(1)

        self.logger.success("Validation passed!")


__all__ = ["Reporter"]
