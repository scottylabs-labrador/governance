import json
from http.client import UNPROCESSABLE_CONTENT
from pathlib import Path
from typing import TYPE_CHECKING

from github import GithubException
from logger import get_app_logger

if TYPE_CHECKING:
    from github import Github, Organization


def populate_issue_types(g: Github, org: Organization) -> None:
    """Populate the issue types for the GitHub organization.

    Uses the issue-types.json file to populate the issue types for the GitHub
    organization. We use a Python script to populate the issue types because
    OpenTofu does not support the issue-types API.
    """
    # Read the issue-types.json file next to this module
    issue_types_path = Path(__file__).with_name("issue-types.json")
    with issue_types_path.open() as f:
        issue_types = json.load(f)

    # We use the low-level requester to call the REST API since
    # the high-level API does not support creating issue types.
    logger = get_app_logger()
    for issue_type in issue_types:
        try:
            g._Github__requester.requestJsonAndCheck(  # noqa: SLF001
                "POST",
                f"/orgs/{org.login}/issue-types",
                input=issue_type,
            )
            logger.success("Created issue type %s", issue_type["name"])
        except GithubException as e:
            if e.status == UNPROCESSABLE_CONTENT:
                logger.info("Issue type %s already exists", issue_type["name"])
                continue
            raise
        except Exception:
            raise
