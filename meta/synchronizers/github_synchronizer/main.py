"""GitHub synchronizer."""

import json
import os

from dotenv import load_dotenv
from github import Github

org_slug = "ScottyLabs"


def main() -> None:
    # """CLI entry point."""
    load_dotenv()
    g = Github(os.getenv("SYNC_GITHUB_TOKEN"))
    # List all issue types in the organization
    org = g.get_organization(org_slug)
    [_, data] = g._Github__requester.requestJsonAndCheck(  # noqa: SLF001
        "GET",
        f"/orgs/{org_slug}/issue-types",
    )
    # write to file
    with open("issue-types.json", "w") as f:
        json.dump(data, f)
