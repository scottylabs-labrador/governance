"""Infrastructure synchronizer.

Generates the input.json file for the infrastructure.
"""

from __future__ import annotations

from typing import Any, override

from dotenv import load_dotenv
from pydantic import BaseModel

from meta.clients.github_client import (
    create_or_update_github_file,
    get_github_client,
)
from meta.logger import print_section
from meta.models import (
    Repo,  # noqa: TC001  # Pydantic needs `Repo` at runtime for `TeamData`.
)

from .abstract import AbstractSynchronizer

# Used for backwards compatibility
LEGACY_DATA = {
    "cmuresearch": {
        "name": "CMU Research",
        "description": "The CMU Research team.",
        "members": {
            "andrew_ids": ["bryung"],
            "github_usernames": [],
        },
        "admins": {
            "andrew_ids": ["bryung"],
            "github_usernames": [],
        },
        "repos": [],
        "create_oidc_clients": True,
    },
    "cmuservice": {
        "name": "CMU Service",
        "description": "The CMU Service team.",
        "members": {
            "andrew_ids": ["benliu"],
            "github_usernames": [],
        },
        "admins": {
            "andrew_ids": ["benliu"],
            "github_usernames": [],
        },
        "repos": [],
        "create_oidc_clients": True,
        "website": "https://cmuservice.shop",
        "server": "https://cmuservice.shop",
    },
    "collegecart": {
        "name": "CollegeCart",
        "description": "The CollegeCart team.",
        "members": {
            "andrew_ids": ["yingyiw", "nayonk", "rushabhj", "rkurihar", "mbatkhuu"],
            "github_usernames": [],
        },
        "admins": {
            "andrew_ids": ["yingyiw", "nayonk", "rushabhj"],
            "github_usernames": [],
        },
        "repos": [],
        "create_oidc_clients": True,
        "website": "https://collegecart.org",
        "server": "https://collegecart.org",
    },
    "cmustudy": {
        "name": "CMU Study",
        "description": "The CMU Study team.",
        "members": {
            "andrew_ids": ["annadavi"],
            "github_usernames": [],
        },
        "admins": {
            "andrew_ids": ["annadavi"],
            "github_usernames": [],
        },
        "repos": [],
        "create_oidc_clients": True,
        "website": "https://study.scottylabs.org",
        "server": "https://study.scottylabs.org",
    },
}


class InfraData(BaseModel):
    """Infrastructure data."""

    members: MembersData
    teams: dict[str, TeamData]


class MembersData(BaseModel):
    """Member data."""

    admins: list[str]
    non_admins: list[str]


class TeamData(BaseModel):
    """Team data."""

    name: str
    description: str
    members: TeamMembersData
    admins: TeamMembersData
    repos: list[Repo]
    create_oidc_clients: bool
    website: str | None = None
    server: str | None = None


class TeamMembersData(BaseModel):
    """Team members data."""

    github_usernames: list[str]
    andrew_ids: list[str]


class InfraSynchronizer(AbstractSynchronizer):
    """Infrastructure synchronizer."""

    INFRA_FILE_PATH = "infra/inputs.json"
    COMMIT_MESSAGE = "chore: auto-update infra/inputs.json"

    def __init__(self) -> None:
        """Initialize the infrastructure synchronizer."""
        super().__init__()
        self.github_client = get_github_client()

    @override
    def sync(self) -> None:
        """Synchronize the infrastructure."""
        print_section("Synchronizing infrastructure")
        create_or_update_github_file(
            self.INFRA_FILE_PATH,
            self.generate_infra_file(),
            self.COMMIT_MESSAGE,
        )

    def generate_infra_file(self) -> str:
        """Generate the infrastructure file."""
        members_data = MembersData(
            admins=self.teams["leadership"].leads,
            non_admins=list(self.members.keys() - self.teams["leadership"].leads),
        )

        teams_data = {}
        for team_slug, team in self.teams.items():
            entry: dict[str, Any] = {
                "name": team.name,
                "description": team.description,
                "members": self._get_users(team.members),
                "admins": self._get_users(team.leads),
                "repos": [repo.model_dump() for repo in team.repos],
                "create_oidc_clients": team.create_oidc_clients,
                "website": team.website,
                "server": team.server,
            }
            teams_data[team_slug] = TeamData.model_validate(entry)

        for team_slug, team_data in LEGACY_DATA.items():
            teams_data[team_slug] = TeamData.model_validate(team_data)

        infra_data = InfraData(
            members=members_data,
            teams=teams_data,
        )
        return infra_data.model_dump_json(indent=2, exclude_none=True) + "\n"

    def _get_users(self, github_usernames: list[str]) -> TeamMembersData:
        """Build users for one team."""
        andrew_ids: list[str] = []
        for github_username in github_usernames:
            member = self.members.get(github_username)
            if member is None or member.andrew_id is None:
                continue
            andrew_ids.append(member.andrew_id)
        return TeamMembersData(github_usernames=github_usernames, andrew_ids=andrew_ids)


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    infra_synchronizer = InfraSynchronizer()
    infra_synchronizer.sync()
