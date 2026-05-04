"""Google Group synchronizer."""

from typing import Any

from dotenv import load_dotenv
from googleapiclient.discovery import build  # type: ignore[import-untyped]

from meta.clients.google_client import GoogleClient
from meta.logger import print_section

from .abstract import AbstractSynchronizer


class GoogleGroupSynchronizer(AbstractSynchronizer):
    """Google Group synchronizer."""

    GROUP_KEY = "sl-labrador@andrew.cmu.edu"

    def __init__(self) -> None:
        """Initialize the Google Group synchronizer."""
        super().__init__()

        google_client = GoogleClient()
        self.google_group_service = build(
            "admin",
            "directory_v1",
            credentials=google_client.creds,
        )

    def sync(self) -> None:
        """Synchronize the google group."""
        print_section("Syncing Google Group")

        members = self.get_all_group_members()
        self.logger.info(
            "ScottyLabs Google Group has %d member(s)",
            len(members),
        )
        for m in members:
            email = m.get("email")
            ident = m.get("id")
            role = m.get("role", "")
            mtype = m.get("type", "")
            label = email or ident or "?"
            self.logger.info("%s (role=%s type=%s)", label, role, mtype)

    def get_all_group_members(self) -> list[dict[str, Any]]:
        """Return every member of the group (paginated Directory API)."""
        members: list[dict[str, Any]] = []
        page_token: str | None = None

        while True:
            response = (
                self.google_group_service.members()
                .list(
                    groupKey=self.GROUP_KEY,
                    maxResults=200,
                    pageToken=page_token,
                )
                .execute()
            )

            members.extend(response.get("members", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return members


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    google_group_synchronizer = GoogleGroupSynchronizer()
    google_group_synchronizer.sync()
