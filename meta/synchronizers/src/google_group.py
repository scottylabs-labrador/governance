"""Google Group Synchronizer.

Uses scottylabs-svc@andrew.cmu.edu as the service account since the Google Group
is managed by CMU.

Uses Cloud Identity API since the credentials are also used by IaC in the Tech
Governance repo and the hashicorp/google module defaults to Cloud Identity.
"""

from __future__ import annotations

import os
import sys
from typing import cast, override

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import discovery  # type: ignore[import-untyped]

from meta.logger import print_section

from .abstract import AbstractSynchronizer


class GoogleGroupSynchronizer(AbstractSynchronizer):
    """Loads OAuth credentials and logs current Google Group memberships."""

    _GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"  # noqa: S105
    GOOGLE_OAUTH_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
    GOOGLE_QUOTA_PROJECT_ID = "sl-governance"
    GOOGLE_GROUP_KEY = "sl-labrador@andrew.cmu.edu"

    def __init__(
        self,
    ) -> None:
        """Initialize Group service using Google OAuth credentials."""
        super().__init__()

        refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        for label, raw in (
            ("GOOGLE_OAUTH_REFRESH_TOKEN", refresh_token),
            ("GOOGLE_OAUTH_CLIENT_ID", client_id),
            ("GOOGLE_OAUTH_CLIENT_SECRET", client_secret),
        ):
            if not raw:
                self.logger.critical("%s is not set", label)
                sys.exit(1)

        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri=self._GOOGLE_TOKEN_URI,
            client_id=client_id,
            client_secret=client_secret,
            scopes=[self.GOOGLE_OAUTH_SCOPE],
            quota_project_id=self.GOOGLE_QUOTA_PROJECT_ID,
        )  # type: ignore[no-untyped-call]
        creds.refresh(Request())
        self.service = discovery.build("cloudidentity", "v1", credentials=creds)

    @override
    def sync(self) -> None:
        print_section("Syncing Google Group")
        members = self.get_member_roles()
        self.logger.info("%s", members)

    def get_member_roles(
        self,
    ) -> dict[str, list[str]]:
        """Create a mapping of Google Group member emails to their roles."""
        parent = self.memberships_parent(self.GOOGLE_GROUP_KEY)
        items = []
        request = (
            self.service.groups()
            .memberships()
            .list(
                parent=parent,
                view="FULL",
                pageSize=200,
            )
        )
        while request is not None:
            response = request.execute()
            items.extend(response.get("memberships", []))
            request = self.service.groups().memberships().list_next(request, response)

        result: dict[str, list[str]] = {}
        for item in items:
            member_email = item["preferredMemberKey"]["id"]
            roles = item["roles"]
            result[member_email] = roles
        return result

    def memberships_parent(self, group_key: str) -> str:
        """Resolve ``groups/{{id}}`` parent for memberships."""
        result = (
            self.service.groups().lookup(groupKey_id=group_key).execute(num_retries=2)
        )
        name = result.get("name")
        if not name:
            msg = "groups.lookup returned no name"
            raise RuntimeError(msg)
        return cast("str", name)


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    GoogleGroupSynchronizer().sync()
