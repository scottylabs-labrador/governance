import json
from pathlib import Path
from typing import TYPE_CHECKING

from logger import log_operation

if TYPE_CHECKING:
    from github import Github, Organization


def sync_issue_types(g: Github, org: Organization) -> None:
    """Sync the issue types for the GitHub organization.

    Uses the issue-types.json file to sync the issue types for the GitHub
    organization. We use a Python script to sync the issue types because
    OpenTofu does not support the issue-types API.

    We use the low-level requester in the GitHub Python library to call the REST
    API since the high-level API does not support creating issue types.
    """
    # Read the issue-types.json file next to this module
    issue_types_path = Path(__file__).with_name("issue-types.json")
    with issue_types_path.open() as f:
        issue_types = json.load(f)

    # Read the existing issue types from the GitHub organization
    with log_operation("reading existing GitHub Organization issue types"):
        [_, existing_issue_types] = g._Github__requester.requestJsonAndCheck(  # noqa: SLF001
            "GET",
            f"/orgs/{org.login}/issue-types",
        )

    # Convert the existing issue types to a dictionary by name
    existing_issue_types = {
        issue_type["name"]: issue_type for issue_type in existing_issue_types
    }

    # Sync the issue types
    for issue_type in issue_types:
        issue_type_name = issue_type["name"]

        # Create the issue type if it does not exist in the GitHub Organization
        if issue_type_name not in existing_issue_types:
            with log_operation(f"creating issue type {issue_type_name}"):
                g._Github__requester.requestJsonAndCheck(  # noqa: SLF001
                    "POST",
                    f"/orgs/{org.login}/issue-types",
                    input=issue_type,
                )
            continue

        # Skip if the issue and existing issue type are exactly the same
        existing_issue_type = existing_issue_types[issue_type_name]
        if issue_type == {
            "name": existing_issue_type["name"],
            "color": existing_issue_type["color"],
            "description": existing_issue_type["description"],
            "is_enabled": existing_issue_type["is_enabled"],
        }:
            continue

        # Since the issue type exists and is different from the existing issue
        # type, update it.
        with log_operation(f"updating issue type {issue_type_name}"):
            g._Github__requester.requestJsonAndCheck(  # noqa: SLF001
                "PUT",
                f"/orgs/{org.login}/issue-types/{existing_issue_type['id']}",
                input=issue_type,
            )
