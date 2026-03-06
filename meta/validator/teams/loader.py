"""Load team TOML files from disk."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomli

from meta.models import Team
from meta.validator.shared.key_ordering import KeyOrdering

if TYPE_CHECKING:
    from meta.validator.shared.reporter import Reporter

TEAMS_GLOB = "teams/*.toml"
TEAM_SCHEMA_PATH = "__meta/schemas/team.schema.json"


def load_teams(reporter: Reporter) -> dict[str, Team]:
    """Load all team TOML files."""
    teams: dict[str, Team] = {}
    key_ordering = KeyOrdering(TEAM_SCHEMA_PATH, reporter)
    for path in sorted(Path().glob(TEAMS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomli.loads(content)
        file_path = f"teams/{path.name}"
        key_ordering.validate(file_path, data)
        team = _load_team(data)
        teams[file_path] = team
    return teams


def _load_team(data: dict[str, Any]) -> Team:
    """Parse one team TOML document."""
    # The schema guarantees that there is at least one membership record.
    first = data.get("membership", [])[0]
    payload: dict[str, Any] = {
        "slug": data["slug"],
        "name": data["name"],
        "website": data.get("website"),
        "create_oidc_clients": data.get("create-oidc-clients", True),
        "repos": [str(repo["name"]) for repo in data.get("repos", [])],
        "maintainers": [str(x) for x in first["maintainers"]],
        "contributors": [
            str(member["github-username"]) for member in first["contributors"]
        ],
    }
    return Team.model_validate(payload)
