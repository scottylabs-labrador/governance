"""Team validation runner."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from meta.models import Contributor, Team
    from meta.validator.shared.reporter import Reporter


class TeamValidator:
    """Run team validation (sync + async) and record results."""

    def __init__(
        self,
        teams: dict[str, Team],
        contributors: dict[str, Contributor],
        reporter: Reporter,
    ) -> None:
        """Create a team validator."""
        self.teams = teams
        self.contributors = contributors
        self.reporter = reporter

    def validate(self) -> None:
        """Run all team validations and record into the reporter."""
        asyncio.run(self.validate_async())
        self.validate_sync()

    async def validate_async(self) -> None:
        """Run async team checks using a fresh HTTP client."""
        async with httpx.AsyncClient() as _:
            pass

    def validate_sync(self) -> None:
        """Run synchronous team checks."""
        self.validate_team_file_names()
        self.validate_maintainers_are_contributors()
        self.validate_cross_references()

    def validate_team_file_names(self) -> None:
        """Validate that team file names match slug."""
        for file_path, team in self.teams.items():
            file_stem = Path(file_path).stem
            if file_stem == team.slug:
                continue

            self.reporter.insert_error(
                file_path,
                f"Team file name '{file_stem}' doesn't match slug '{team.slug}'",
            )

    def validate_maintainers_are_contributors(self) -> None:
        """Ensure every maintainer is also listed as a contributor."""
        for team_file, team in self.teams.items():
            contributor_set = set(team.contributors)
            for maintainer in team.maintainers:
                if maintainer in contributor_set:
                    continue

                self.reporter.insert_error(
                    team_file,
                    f"Maintainer {maintainer!r} missing from contributors",
                )

    def validate_cross_references(self) -> None:
        """Check that all team contributors exist in contributors."""
        for team_file, team in self.teams.items():
            for contributor in team.contributors:
                contributor_file = f"contributors/{contributor}.toml"
                if contributor_file in self.contributors:
                    continue

                self.reporter.insert_error(
                    team_file,
                    f"Unknown contributor: {contributor}",
                )
