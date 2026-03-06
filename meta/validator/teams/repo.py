# ruff: noqa: ERA001  # noqa: D100

# """Validation checks for teams."""

# from __future__ import annotations

# import asyncio
# import os
# from typing import TYPE_CHECKING

# import httpx

# if TYPE_CHECKING:
#     from meta.models import Team
#     from meta.validator.shared.reporter import Reporter


# USER_AGENT = "ScottyLabs-Governance-Validator"
# GITHUB_ORG = "scottylabs-labrador"

# HTTP_OK = 200
# HTTP_NOT_FOUND = 404
# HTTP_FORBIDDEN = 403


# class RepoCheckResult:
#     """Result types for GitHub repository existence checks."""

#     EXISTS_IN_ORG = "exists_in_org"
#     EXISTS_OUTSIDE_ORG = "exists_outside_org"
#     NOT_FOUND = "not_found"


# async def validate_github_repositories(
#     reporter: Reporter,
#     teams: dict[str, Team],
#     client: httpx.AsyncClient,
# ) -> None:
#     """Validate that team repos exist and are in ScottyLabs org."""

#     async def check_one(repository: str) -> str | None:
#         return await _check_github_repository_exists(repository, client)

#     keys_repos = [
#         (team_file, repo_name, f"{GITHUB_ORG}/{repo_name}")
#         for team_file, team in teams.items()
#         for repo_name in team.repos
#     ]

#     results = await asyncio.gather(
#         *(check_one(repository) for _, _, repository in keys_repos),
#     )

#     for (team_file, repo_name, _), (result_type, org, err_msg) in zip(
#         keys_repos,
#         results,
#         strict=False,
#     ):
#         if err_msg:
#             reporter.insert_error(
#                 team_file,
#                 f"Failed to check GitHub repository {repo_name}: {err_msg}",
#             )
#             continue

#         err = _repo_validation_error(team_file, repo_name, result_type, org)
#         if err is not None:
#             file_path, message = err
#             reporter.insert_error(file_path, message)


# async def _check_github_repository_exists(
#     repo: str, client: httpx.AsyncClient
# ) -> str | None:
#     r"""Return an error message if the repository is not valid."""
#     token = os.environ.get("SYNC_GITHUB_TOKEN", "")
#     try:
#         headers = {"User-Agent": USER_AGENT}
#         if token:
#             headers["Authorization"] = f"Bearer {token}"
#         r = await client.get(
#             f"https://api.github.com/repos/{repository}",
#             headers=headers,
#         )
#         if r.status_code == HTTP_OK:
#             data = r.json()
#             org_login = (data.get("organization") or {}).get("login")
#             if org_login != GITHUB_ORG:
#                 return f'GitHub repository {repo_name} is not in the "{GITHUB_ORG}" '
#                 f"organization. It is in the {org} organization."

#             return None

#         if r.status_code == HTTP_NOT_FOUND:
#             return f"GitHub repository does not exist: {repo_name}"

#         if r.status_code == HTTP_FORBIDDEN:
#             raise GitHubRateLimitedOrForbiddenError

#         raise GitHubUnexpectedStatusError(r.status_code)

#     except httpx.HTTPError as e:
#         raise GitHubRequestError(e) from e


# def _repo_validation_error(
#     file_path: str,
#     repo_name: str,
#     result_type: str,
#     org: str | None,
# ) -> tuple[str, str] | None:
#     if result_type == RepoCheckResult.EXISTS_OUTSIDE_ORG and org:
#         return (
#             file_path,
#             f'GitHub repository {repo_name} is not in the "{GITHUB_ORG}" '
#             f"organization. It is in the {org} organization.",
#         )
#     if result_type == RepoCheckResult.NOT_FOUND:
#         return (file_path, f"GitHub repository does not exist: {repo_name}")
#     return None
