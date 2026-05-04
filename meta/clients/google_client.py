"""Google Drive client."""

import os
from typing import ClassVar, Literal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# The type checking performance after installing the stubs is so bad it is faster to
# develope without them...
# https://github.com/henribru/google-api-python-client-stubs?tab=readme-ov-file#performance
from meta.logger import get_app_logger

_GROUP_SCOPE: tuple[str, ...] = (
    "https://www.googleapis.com/auth/admin.directory.group.member",
)


class GoogleClient:
    """Google client."""

    DRIVE_ROLE = Literal["writer", "fileOrganizer"]
    DRIVE_ROLE_TO_ROLE_NAME: ClassVar[dict[DRIVE_ROLE, str]] = {
        "writer": "contributor",
        "fileOrganizer": "content manager",
    }

    def __init__(
        self,
    ) -> None:
        """Initialize the Google client from OAuth user credentials."""
        logger = get_app_logger()

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

        missing = [
            name
            for name, val in (
                ("GOOGLE_CLIENT_ID", client_id),
                ("GOOGLE_CLIENT_SECRET", client_secret),
                ("GOOGLE_REFRESH_TOKEN", refresh_token),
            )
            if not val
        ]
        if missing:
            msg = f"Missing required env var(s): {', '.join(missing)}"
            logger.critical(msg)
            raise RuntimeError(msg)

        info = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "type": "authorized_user",
        }

        self.creds = Credentials.from_authorized_user_info(info, scopes=_GROUP_SCOPE)  # type: ignore[no-untyped-call]
        if self.creds is None:
            msg = "Could not build OAuth user credentials from env vars"
            logger.critical(msg)
            raise RuntimeError(msg)

        if not self.creds.valid:
            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                msg = (
                    "Google credentials are invalid or expired and cannot be refreshed"
                )
                logger.critical(msg)
                raise RuntimeError(msg)
