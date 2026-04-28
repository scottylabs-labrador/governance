"""Tests for the governance validator package."""

import subprocess


def main() -> None:
    """Test the validator."""
    subprocess.run(
        [  # noqa: S607
            "pytest",
            "meta/validator/tests",
            "--cov=meta/validator/src/members",
            "--cov=meta/validator/src/teams",
            "--cov=meta/validator/src/shared",
            "--cov-report=term-missing",
        ],
        check=True,
    )


__all__ = ["main"]
