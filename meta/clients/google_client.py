"""Google Drive client."""

import os
from typing import ClassVar, Literal

from google.oauth2 import service_account

# The type checking performance after installing the stubs is so bad it is faster to
# develope without them...
# https://github.com/henribru/google-api-python-client-stubs?tab=readme-ov-file#performance
from googleapiclient.discovery import build  # type: ignore[import-untyped]

from meta.logger import get_app_logger


class GoogleClient:
    """Google Drive client."""

    DRIVE_ROLE = Literal["writer", "fileOrganizer"]
    DRIVE_ROLE_TO_ROLE_NAME: ClassVar[dict[DRIVE_ROLE, str]] = {
        "writer": "contributor",
        "fileOrganizer": "content manager",
    }

    GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"  # noqa: S105

    def __init__(
        self,
    ) -> None:
        """Initialize the Google Drive synchronizer."""
        logger = get_app_logger()

        google_client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
        google_private_key = os.getenv("GOOGLE_PRIVATE_KEY")

        if not google_client_email:
            msg = "GOOGLE_CLIENT_EMAIL is not set"
            logger.critical(msg)
            raise RuntimeError(msg)

        if not google_private_key:
            msg = "GOOGLE_PRIVATE_KEY is not set"
            logger.critical(msg)
            raise RuntimeError(msg)

        creds = service_account.Credentials.from_service_account_info(  # type: ignore[no-untyped-call]
            info={
                "private_key": google_private_key,
                "client_email": google_client_email,
                "token_uri": self.GOOGLE_TOKEN_URI,
            },
        )

        self.drive_service = build("drive", "v3", credentials=creds)
