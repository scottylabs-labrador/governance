"""GitHub synchronizer."""

import os

from dotenv import load_dotenv

from github import Github

from ._issue_types import sync_issue_types

org_slug = "ScottyLabs-Labrador"


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    g = Github(os.getenv("SYNC_GITHUB_TOKEN"))
    org = g.get_organization(org_slug)
    sync_issue_types(g, org)
