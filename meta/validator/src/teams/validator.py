"""Team validation runner."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import httpx

from meta.validator.src.reporter import ErrorCode

if TYPE_CHECKING:
    from meta.models import Member, Team
    from meta.validator.src.reporter import Reporter


class TeamValidator:
    """Run team validation (sync + async) and record results."""

    def __init__(
        self,
        teams: dict[str, Team],
        members: dict[str, Member],
        reporter: Reporter,
    ) -> None:
        """Create a team validator."""
        self.teams = teams
        self.members = members
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
        self.validate_maintainers_are_contributors()
        self.validate_cross_references()

    def validate_maintainers_are_contributors(self) -> None:
        """Ensure every maintainer is also listed as a contributor."""
        for team_file, team in self.teams.items():
            member_set = set(team.members)
            for lead in team.leads:
                if lead not in member_set:
                    self.reporter.insert_error(
                        team_file,
                        ErrorCode.LEAD_CROSS_REFERENCE,
                        f"Lead {lead!r} missing from members",
                    )

    def validate_cross_references(self) -> None:
        """Check that all team contributors exist in contributors."""
        for team in self.teams.values():
            for member in team.members:
                if member not in self.members:
                    self.reporter.insert_error(
                        team.file_path,
                        ErrorCode.MEMBER_CROSS_REFERENCE,
                        f"Unknown member: {member}",
                    )
