"""Slack client."""

import os
import ssl
import sys
from typing import cast

import certifi
from slack_sdk import WebClient

from meta.logger import get_app_logger


class SlackClient:
    """Slack client.

    Slack SDK methods not defined here are forwarded to :class:`slack_sdk.WebClient`
    (e.g. ``conversations_create``, ``conversations_invite``).
    """

    def __init__(self, env_var_name: str) -> None:
        """Initialize the Slack client."""
        self.logger = get_app_logger()

        slack_token = os.getenv(env_var_name)
        if not slack_token:
            msg = f"{env_var_name} is not set"
            self.logger.critical(msg)
            sys.exit(1)

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(token=slack_token, ssl=ssl_context)

    def get_all_channels(self) -> list[dict[str, str]]:
        """Get all channels channels and their IDs."""
        channels: list[dict[str, str]] = []
        cursor: str | None = None
        while True:
            response = self.client.conversations_list(
                types="public_channel",
                cursor=cursor,
            )

            channels.extend(
                {"id": channel["id"], "name": channel["name"]}
                for channel in response["channels"]
            )

            metadata = cast(
                "dict[str, object]",
                response.get("response_metadata"),
            )
            cursor = cast("str | None", metadata.get("next_cursor"))
            if not cursor:
                break

        return channels
