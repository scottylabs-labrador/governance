"""Google synchronizer."""

import os
from typing import override

from dotenv import load_dotenv
from googleapiclient.discovery import build  # type: ignore[import-untyped]

from meta.clients.google_client import GoogleClient
from meta.logger import print_section

from .abstract import AbstractSynchronizer


class GoogleDriveSynchronizer(AbstractSynchronizer):
    """Google Drive synchronizer."""

    def __init__(self) -> None:
        """Initialize the Google Drive synchronizer."""
        super().__init__()

        self.google_drive_id = os.getenv("SCOTTYLABS_GOOGLE_DRIVE_ID")
        if not self.google_drive_id:
            msg = "SCOTTYLABS_GOOGLE_DRIVE_ID is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        google_client = GoogleClient()
        self.google_drive_service = build(
            "drive",
            "v3",
            credentials=google_client.creds,
        )

    @override
    def sync(self) -> None:
        """Synchronize the google drive."""
        print_section("Syncing Google Drive")

        self.get_all_drive_permissions()

    def get_all_drive_permissions(self) -> dict[str, str]:
        """Return a email to role mapping for the ScottyLabs Google Drive."""
        permissions = {}
        page_token = None

        while True:
            response = (
                self.google_drive_service.permissions()
                .list(
                    fileId=self.google_drive_id,
                    fields="nextPageToken, permissions(emailAddress,role)",
                    supportsAllDrives=True,
                    pageToken=page_token,
                )
                .execute()
            )

            for permission in response.get("permissions", []):
                email_address = permission["emailAddress"]
                role = permission["role"]
                permissions[email_address] = role

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return permissions


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    google_drive_synchronizer = GoogleDriveSynchronizer()
    google_drive_synchronizer.sync()
