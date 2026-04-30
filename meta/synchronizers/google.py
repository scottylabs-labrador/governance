"""Google synchronizer."""

import os
from typing import override

from dotenv import load_dotenv

from meta.clients.google_client import GoogleClient
from meta.logger import print_section

from .abstract import AbstractSynchronizer


class GoogleSynchronizer(AbstractSynchronizer):
    """Google synchronizer."""

    def __init__(self) -> None:
        """Initialize the google synchronizer."""
        super().__init__()

        self.google_client = GoogleClient()

        scottylabs_google_drive_id = os.getenv("SCOTTYLABS_GOOGLE_DRIVE_ID")
        if not scottylabs_google_drive_id:
            msg = "SCOTTYLABS_GOOGLE_DRIVE_ID is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        self.google_drive_id = scottylabs_google_drive_id

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
                self.google_client.drive_service.permissions()
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
    google_synchronizer = GoogleSynchronizer()
    google_synchronizer.sync()
