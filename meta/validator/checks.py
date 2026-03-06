"""Validation checks for contributors and teams."""

import logging
import os
from typing import Protocol

import httpx

from .model import (
    Contributor,
    EntityKey,
    Team,
    ValidationError,
    ValidationWarning,
)

logger = logging.getLogger(__name__)

USER_AGENT = "ScottyLabs-Governance-Validator"
SCOTTYLABS_ORG = "ScottyLabs"


class HasKeyOrder(Protocol):
    def get_key_order(self) -> list[str]: ...
    def set_key_order(self, order: list[str]) -> None: ...


def _is_subsequence_in_order(actual_order: list[str], expected_order: list[str]) -> bool:
    """Check that actual_order is a subsequence of expected_order in the right order."""
    i = 0
    for a in actual_order:
        while i < len(expected_order) and expected_order[i] != a:
            i += 1
        if i == len(expected_order):
            return False
        i += 1
    return True


def validate_key_orderings(
    data: dict[EntityKey, HasKeyOrder],
    expected_order: list[str],
) -> list[ValidationError]:
    """Validate key order in TOML files against the expected schema order."""
    if not data:
        return [
            ValidationError(file="N/A", message="No data found"),
        ]
    kind = next(iter(data.keys())).kind
    logger.info("Validating %s key orderings...", kind)
    errors: list[ValidationError] = []
    for key, item in data.items():
        actual_order = item.get_key_order()
        if not _is_subsequence_in_order(actual_order, expected_order):
            file_path = f"{kind}s/{key.name}.toml"
            errors.append(
                ValidationError(
                    file=file_path,
                    message=(
                        f"Invalid key order for {key}.\n"
                        f"    - expected (schema): {expected_order}\n"
                        f"    - found (file): {actual_order}"
                    ),
                )
            )
    return errors


def validate_file_names(
    contributors: dict[EntityKey, Contributor],
    teams: dict[EntityKey, Team],
) -> list[ValidationError]:
    """Validate that file names match GitHub username (contributors) or slug (teams)."""
    logger.info("Validating file names...")
    errors: list[ValidationError] = []
    for key, contributor in contributors.items():
        if key.name != contributor.github_username:
            errors.append(
                ValidationError(
                    file=f"contributors/{key.name}.toml",
                    message=(
                        f"Contributor file name '{key.name}' doesn't match "
                        f"GitHub username '{contributor.github_username}'"
                    ),
                )
            )
    for key, team in teams.items():
        if key.name != team.slug:
            errors.append(
                ValidationError(
                    file=f"teams/{key.name}.toml",
                    message=(
                        f"Team file name '{key.name}' doesn't match slug '{team.slug}'"
                    ),
                )
            )
    return errors


def validate_maintainers_are_contributors(
    teams: dict[EntityKey, Team],
) -> list[ValidationError]:
    """Ensure every maintainer is also listed as a contributor."""
    logger.info("Validating that all maintainers are also contributors...")
    errors: list[ValidationError] = []
    for team_key, team in teams.items():
        contributor_set = set(team.contributors)
        for maintainer in team.maintainers:
            if maintainer not in contributor_set:
                errors.append(
                    ValidationError(
                        file=f"teams/{team_key.name}.toml",
                        message=f"Maintainer '{maintainer}' is not a contributor",
                    )
                )
    return errors


def validate_cross_references(
    contributors: dict[EntityKey, Contributor],
    teams: dict[EntityKey, Team],
) -> list[ValidationError]:
    """Check that all team participants exist in contributors."""
    logger.info("Validating cross-references...")
    errors: list[ValidationError] = []
    for team_key, team in teams.items():
        participants = list(team.maintainers) + list(team.contributors)
        if team.applicants:
            participants.extend(team.applicants)
        for participant in participants:
            key = EntityKey(kind="contributor", name=participant)
            if key not in contributors:
                errors.append(
                    ValidationError(
                        file=f"teams/{team_key.name}.toml",
                        message=(
                            f"Team '{team_key.name}' references non-existent "
                            f"contributor: {participant}"
                        ),
                    )
                )
    return errors


async def _check_github_user_exists(github_username: str, client: httpx.AsyncClient) -> bool | None:
    """Return True if user exists, False if not found, None on request error."""
    token = os.environ.get("SYNC_GITHUB_TOKEN", "")
    try:
        headers = {"User-Agent": USER_AGENT}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = await client.get(
            f"https://api.github.com/users/{github_username}",
            headers=headers,
        )
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        if r.status_code == 403:
            raise ValueError("Rate limit exceeded or access forbidden")
        raise ValueError(f"Unexpected status {r.status_code}")
    except httpx.HTTPError as e:
        raise ValueError(str(e)) from e


async def validate_github_users(
    contributors: dict[EntityKey, Contributor],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate that all contributor GitHub usernames exist."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    import asyncio

    items = list(contributors.items())

    async def check_one(key: EntityKey, github: str):
        try:
            exists = await _check_github_user_exists(github, client)
            if exists is False:
                return ("error", key, f"GitHub user does not exist: {github}")
            return (None, None, None)
        except ValueError as e:
            return ("warning", key, f"Failed to check GitHub user {github}: {e}")

    tasks = [check_one(key, c.github_username) for key, c in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        key = items[i][0]
        file_path = f"contributors/{key.name}.toml"
        if isinstance(res, BaseException):
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check GitHub user: {res}",
                )
            )
            continue
        kind, _, msg = res
        if kind == "error" and msg:
            errors.append(ValidationError(file=file_path, message=msg))
        elif kind == "warning" and msg:
            warnings.append(ValidationWarning(file=file_path, message=msg))
    return (errors, warnings)


class RepoCheckResult:
    EXISTS_IN_ORG = "exists_in_org"
    EXISTS_OUTSIDE_ORG = "exists_outside_org"
    NOT_FOUND = "not_found"


async def _check_github_repository_exists(
    repository: str,
    client: httpx.AsyncClient,
) -> tuple[str, str | None]:
    """Return (result_type, org_or_none). result_type: exists_in_org, exists_outside_org, not_found."""
    token = os.environ.get("SYNC_GITHUB_TOKEN", "")
    try:
        headers = {"User-Agent": USER_AGENT}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = await client.get(
            f"https://api.github.com/repos/{repository}",
            headers=headers,
        )
        if r.status_code == 200:
            data = r.json()
            org_login = (data.get("organization") or {}).get("login")
            if org_login == "ScottyLabs":
                return (RepoCheckResult.EXISTS_IN_ORG, None)
            return (RepoCheckResult.EXISTS_OUTSIDE_ORG, org_login or "<no org>")
        if r.status_code == 404:
            return (RepoCheckResult.NOT_FOUND, None)
        if r.status_code == 403:
            raise ValueError("Rate limit exceeded or access forbidden")
        raise ValueError(f"Unexpected status {r.status_code}")
    except httpx.HTTPError as e:
        raise ValueError(str(e)) from e


async def validate_github_repositories(
    teams: dict[EntityKey, Team],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate that team repos exist and are in ScottyLabs org."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    import asyncio

    async def check_one(team_key: EntityKey, repo: str):
        try:
            result_type, org = await _check_github_repository_exists(repo, client)
            return (team_key, repo, result_type, org, None)
        except ValueError as e:
            return (team_key, repo, "error", None, str(e))

    tasks = []
    keys_repos: list[tuple[EntityKey, str]] = []
    for team_key, team in teams.items():
        for repo in team.repos:
            tasks.append(check_one(team_key, repo))
            keys_repos.append((team_key, repo))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        team_key, repo = keys_repos[i]
        file_path = f"teams/{team_key.name}.toml"
        if isinstance(res, BaseException):
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check GitHub repository {repo}: {res}",
                )
            )
            continue
        _, _, result_type, org, err_msg = res
        if err_msg:
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check GitHub repository {repo}: {err_msg}",
                )
            )
            continue
        if result_type == RepoCheckResult.EXISTS_OUTSIDE_ORG and org:
            errors.append(
                ValidationError(
                    file=file_path,
                    message=(
                        f'GitHub repository {repo} is not in the "{SCOTTYLABS_ORG}" '
                        f"organization. It is in the {org} organization."
                    ),
                )
            )
        elif result_type == RepoCheckResult.NOT_FOUND:
            errors.append(
                ValidationError(
                    file=file_path,
                    message=f"GitHub repository does not exist: {repo}",
                )
            )
    return (errors, warnings)


async def _check_slack_id_exists(slack_id: str, client: httpx.AsyncClient) -> bool | None:
    """Return True if exists, False if not found, raise on auth/rate limit."""
    token = os.environ.get("SLACK_TOKEN", "")
    if not token:
        raise ValueError("SLACK_TOKEN environment variable not set")
    if slack_id.startswith("U"):
        endpoint = "https://slack.com/api/users.info"
        param_name = "user"
    elif slack_id.startswith("C") or slack_id.startswith("G"):
        endpoint = "https://slack.com/api/conversations.info"
        param_name = "channel"
    else:
        raise ValueError(f"Invalid Slack ID format: {slack_id}")

    r = await client.get(
        endpoint,
        params={param_name: slack_id},
        headers={"User-Agent": USER_AGENT, "Authorization": f"Bearer {token}"},
    )
    data = r.json()
    ok = data.get("ok")
    if ok is True:
        return True
    if ok is False:
        err = data.get("error", "")
        if err in ("user_not_found", "channel_not_found"):
            return False
        if err == "ratelimited":
            raise ValueError("Rate limit exceeded")
        if err == "invalid_auth":
            raise ValueError("Invalid authentication")
        raise ValueError(f"Slack API error: {err}")
    raise ValueError("Unexpected response from Slack API")


async def validate_slack_ids(
    contributors: dict[EntityKey, Contributor],
    teams: dict[EntityKey, Team],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate Slack member IDs (contributors) and channel IDs (teams)."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    import asyncio

    # Contributor Slack member IDs
    async def check_contributor_slack(key: EntityKey, slack_id: str):
        try:
            exists = await _check_slack_id_exists(slack_id, client)
            return ("contributor", key, slack_id, exists, None)
        except ValueError as e:
            return ("contributor", key, slack_id, None, str(e))

    tasks = []
    items = []
    for key, c in contributors.items():
        if c.slack_member_id:
            tasks.append(check_contributor_slack(key, c.slack_member_id))
            items.append(("contributor", key, c.slack_member_id))

    # Team Slack channel IDs
    async def check_team_channel(team_key: EntityKey, channel_id: str):
        try:
            exists = await _check_slack_id_exists(channel_id, client)
            return ("team", team_key, channel_id, exists, None)
        except ValueError as e:
            return ("team", team_key, channel_id, None, str(e))

    for team_key, team in teams.items():
        for channel_id in team.slack_channel_ids:
            tasks.append(check_team_channel(team_key, channel_id))
            items.append(("team", team_key, channel_id))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        if isinstance(res, BaseException):
            kind, key, sid = items[i]
            file_path = f"{'contributors' if kind == 'contributor' else 'teams'}/{key.name}.toml"
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check Slack ID {sid}: {res}",
                )
            )
            continue
        kind, key, sid, exists, err_msg = res
        file_path = f"{'contributors' if kind == 'contributor' else 'teams'}/{key.name}.toml"
        if err_msg:
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check Slack ID {sid}: {err_msg}",
                )
            )
            continue
        if exists is False:
            label = "Slack member ID" if kind == "contributor" else "Slack channel ID"
            errors.append(
                ValidationError(
                    file=file_path,
                    message=f"{label} does not exist: {sid}",
                )
            )
    return (errors, warnings)
