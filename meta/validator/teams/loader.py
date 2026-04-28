"""Load team TOML files from disk."""

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from meta.models import Team
from meta.validator.shared import KeyOrdering

if TYPE_CHECKING:
    from meta.validator.shared.reporter import Reporter

TEAMS_GLOB = "teams/*.toml"
TEAM_SCHEMA_PATH = "meta/schemas/team.schema.json"


def load_teams(
    reporter: Reporter,
    teams_glob: str = TEAMS_GLOB,
) -> dict[str, Team]:
    """Load all team TOML files."""
    teams: dict[str, Team] = {}
    key_ordering = KeyOrdering(TEAM_SCHEMA_PATH, reporter)
    for path in sorted(Path().glob(teams_glob)):
        if not path.is_file():
            reporter.insert_error(path.name, "Not a file")

        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomllib.loads(content)
        file_path = f"teams/{path.name}"
        key_ordering.validate(file_path, data)
        team = _load_team(file_path, data)
        team_slug = path.stem
        teams[team_slug] = Team.model_validate(team)

    return teams


def _load_team(file_path: str, data: dict[str, Any]) -> Team:
    """Parse one team TOML document."""
    # The schema guarantees that there is at least one membership record.
    first = data.get("membership", [])[0]
    payload: dict[str, Any] = {
        "name": data["name"],
        "website": data.get("website"),
        "server": data.get("server"),
        "create_oidc_clients": data.get("create-oidc-clients", True),
        "repos": [str(repo["name"]) for repo in data.get("repos", [])],
        "leads": [str(x) for x in first["leads"]],
        "members": [str(member["github-username"]) for member in first["members"]],
        "file_path": file_path,
    }
    return Team.model_validate(payload)
