"""Infrastructure synchronizer.

Generates the input.json file for the infrastructure.
"""

from __future__ import annotations

import json
from typing import Any, override

from dotenv import load_dotenv

from meta.clients.github_client import (
    create_or_update_github_file,
    get_github_client,
)
from meta.logger import print_section

from .abstract import AbstractSynchronizer

# Used for backwards compatibility
LEGACY_TEAMS_DATA = {
    "cmuresearch": {
        "members": {
            "andrew-ids": ["bryung"],
            "github-usernames": [],
        },
        "admins": {
            "andrew-ids": ["bryung"],
            "github-usernames": [],
        },
    },
    "cmuservice": {
        "members": {
            "andrew-ids": ["benliu"],
            "github-usernames": [],
        },
        "admins": {
            "andrew-ids": ["benliu"],
            "github-usernames": [],
        },
        "website": "https://cmuservice.shop",
        "server": "https://cmuservice.shop",
    },
    "collegecart": {
        "members": {
            "andrew-ids": ["yingyiw", "nayonk", "rushabhj", "rkurihar", "mbatkhuu"],
            "github-usernames": [],
        },
        "admins": {
            "andrew-ids": ["yingyiw", "nayonk", "rushabhj"],
            "github-usernames": [],
        },
        "website": "https://collegecart.org",
        "server": "https://collegecart.org",
    },
    "cmustudy": {
        "members": [
            "annadavi",
        ],
        "admins": [
            "annadavi",
        ],
        "website": "https://study.scottylabs.org",
        "server": "https://study.scottylabs.org",
    },
}


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
        data: dict[str, Any] = {}
        data["leadership"] = {
            "members": self._get_users(self.teams["leadership"].members),
            "admins": self._get_users(self.teams["leadership"].leads),
        }
        data["teams"] = {
            team_slug: {
                "members": self._get_users(team.members),
                "admins": self._get_users(team.leads),
                "website": team.website,
                "server": team.server,
            }
            for team_slug, team in self.teams.items()
            if team_slug != "leadership"
        }

        for team_slug, team_data in LEGACY_TEAMS_DATA.items():
            data["teams"][team_slug] = team_data  # ty:ignore[invalid-assignment]

        return json.dumps(data, indent=2) + "\n"

    def _get_users(self, github_usernames: list[str]) -> dict[str, list[str]]:
        """Build users for one team."""
        users: dict[str, list[str]] = {
            "github_usernames": [],
            "andrew_ids": [],
        }
        for github_username in github_usernames:
            users["github_usernames"].append(github_username)
            member = self.members.get(github_username)
            if member is None or member.andrew_id is None:
                continue
            users["andrew_ids"].append(member.andrew_id)
        return users


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    infra_synchronizer = InfraSynchronizer()
    infra_synchronizer.sync()
