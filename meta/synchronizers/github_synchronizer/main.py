"""GitHub synchronizer."""

import os

from dotenv import load_dotenv
from github import Github

from ._populator import populate_issue_types

org_slug = "ScottyLabs-Labrador"


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    g = Github(os.getenv("SYNC_GITHUB_TOKEN"))
    org = g.get_organization(org_slug)
    populate_issue_types(g, org)
